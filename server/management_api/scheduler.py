from datetime import datetime
import pytz
from django.db import connection
from django.utils import timezone
from ping3 import ping as ping_host

def create_schedule_task():
    from django_q.models import Schedule

    task_configs = [
        'management_api.scheduler.charge_users_for_active_servers_and_services',
        'management_api.scheduler.check_server_and_service_online_status',
        'management_api.scheduler.check_expiry_timestamp_on_servers_and_services',
        'management_api.scheduler.scheduled_credits_to_users',
        'management_api.scheduler.check_user_balance_for_servers_and_services_without_timestamp',
        'management_api.scheduler.process_platform_settings_recharge',
    ]

    for task_func in task_configs:
        if not Schedule.objects.filter(func=task_func).exists():
            Schedule.objects.create(
                func=task_func,
                schedule_type=Schedule.MINUTES,
                minutes=1,
                repeats=-1,
                next_run=timezone.now()
            )

            print(f"Task {task_func} successfully created")


def charge_users_for_active_servers_and_services():
    from server_api.models import Server
    from service_api.models import Service
    from django_q.tasks import async_task
    from infra.Terraform.server_manager import delete_server_terraform
    from infra.Terraform.container_manager import delete_container
    from django.contrib.auth import get_user_model

    try:
        User = get_user_model()
        user_coin_changes = {}

        active_servers = Server.objects.select_related('owner', 'server_config').filter(unlimited=False, is_deleted=False).exclude(status='creating')
        active_services = Service.objects.select_related('owner', 'service_config__server_config').filter(unlimited=False, is_deleted=False).exclude(status='creating')

        for server in active_servers:
            user = server.owner
            cost = server.server_config.cost_per_hour

            if user.coins >= cost:
                user_coin_changes[user.id] = user_coin_changes.get(user.id, user.coins) - cost
            else:
                async_task(delete_server_terraform, server, server.id, server.server_config.script, "insufficient_funds",
                           hook='core.task_handlers.handle_server_delete_result')

        for service in active_services:
            user = service.owner
            server_config = service.service_config.server_config
            cost = server_config.cost_per_hour

            if user.coins >= cost:
                user_coin_changes[user.id] = user_coin_changes.get(user.id, user.coins) - cost
            else:
                async_task(delete_container, service, service.id, service.hostname, server_config.script, "insufficient_funds",
                           hook='core.task_handlers.handle_service_delete_result')

        if user_coin_changes:
            users = User.objects.filter(id__in=user_coin_changes.keys())
            for user in users:
                user.coins = user_coin_changes[user.id]
            User.objects.bulk_update(users, ['coins'])

    finally:
        connection.close()


def check_server_and_service_online_status():
    from server_api.models import Server
    from service_api.models import Service

    try:
        servers = Server.objects.exclude(ip_address__isnull=True).exclude(ip_address="").exclude(is_deleted=True).exclude(status='creating')
        services = Service.objects.exclude(ip_address__isnull=True).exclude(ip_address="").exclude(is_deleted=True).exclude(status='creating')

        servers_to_update = []
        services_to_update = []

        for server in servers:
            is_online = ping(server.ip_address)
            server.vps_status = "online" if is_online else "offline"
            servers_to_update.append(server)

        for service in services:
            is_online = ping(service.ip_address)
            service.vps_status = "online" if is_online else "offline"
            services_to_update.append(service)

        Server.objects.bulk_update(servers_to_update, ['vps_status'])
        Service.objects.bulk_update(services_to_update, ['vps_status'])
    finally:
        connection.close()

def check_expiry_timestamp_on_servers_and_services():
    from server_api.models import Server
    from django_q.tasks import async_task
    from infra.Terraform.server_manager import delete_server_terraform
    from service_api.models import Service
    from core.mail_utils import send_server_expiry_warning_email, send_service_expiry_warning_email
    from infra.Terraform.container_manager import delete_container

    try:
        now = timezone.now()
        now_date = now.date()
        warning_days = [7, 3, 1]

        servers = Server.objects.select_related('owner', 'server_config').filter(expiry_timestamp__isnull=False, is_deleted=False).exclude(status='creating')
        services = Service.objects.select_related('owner', 'service_config__server_config').filter(expiry_timestamp__isnull=False, is_deleted=False).exclude(status='creating')

        for server in servers:
            expiry_date = timezone.make_aware(datetime.utcfromtimestamp(server.expiry_timestamp), pytz.UTC)
            days_left = (expiry_date.date() - now_date).days

            if days_left in warning_days:
                send_server_expiry_warning_email(server, expiry_date, days_left)

            if expiry_date <= now:
                async_task(delete_server_terraform, server, server.id, server.server_config.script, "insufficient_funds",
                           hook='core.task_handlers.handle_server_delete_result')

        for service in services:
            expiry_date = timezone.make_aware(datetime.utcfromtimestamp(service.expiry_timestamp), pytz.UTC)
            days_left = (expiry_date.date() - now_date).days

            if days_left in warning_days:
                send_service_expiry_warning_email(service, expiry_date, days_left)

            if expiry_date <= now:
                script = service.service_config.server_config.script
                async_task(delete_container, service, service.id, service.hostname, script, "insufficient_funds",
                           hook='core.task_handlers.handle_service_delete_result')
    finally:
        connection.close()

def check_user_balance_for_servers_and_services_without_timestamp():
    from user_api.models import User
    from server_api.models import Server
    from service_api.models import Service
    from core.mail_utils import send_expiry_warning_email_without_timestamp

    try:
        user_ids = set(Server.objects.values_list('owner_id', flat=True)) | set(Service.objects.values_list('owner_id', flat=True))
        users = User.objects.filter(id__in=user_ids)

        warning_days = [7, 3, 1]

        for user in users:
            servers = Server.objects.select_related('server_config').filter(owner=user, is_deleted=False).exclude(status='creating')
            services = Service.objects.select_related('service_config__server_config').filter(owner=user, is_deleted=False).exclude(status='creating')

            daily_cost = sum(s.server_config.cost_per_hour * 24 for s in servers)
            daily_cost += sum(s.service_config.server_config.cost_per_hour * 24 for s in services)

            servers_without_ts = servers.filter(expiry_timestamp__isnull=True)
            services_without_ts = services.filter(expiry_timestamp__isnull=True)

            servers_to_warn = []
            services_to_warn = []

            for server in servers_without_ts:
                total_cost = daily_cost + server.server_config.cost_per_hour * 24
                days_left = (user.coins // total_cost) if total_cost > 0 else float('inf')
                if days_left in warning_days:
                    servers_to_warn.append((server, days_left))

            for service in services_without_ts:
                cost = service.service_config.server_config.cost_per_hour * 24
                total_cost = daily_cost + cost
                days_left = (user.coins // total_cost) if total_cost > 0 else float('inf')
                if days_left in warning_days:
                    services_to_warn.append((service, days_left))

            if servers_to_warn or services_to_warn:
                send_expiry_warning_email_without_timestamp(user, servers_to_warn, services_to_warn)
    finally:
        connection.close()



def scheduled_credits_to_users():
    from management_api.models import ScheduledCredit
    from user_api.models import User
    from management_api.models import PlattformSettings
    from django.db import transaction

    try:
        now = timezone.now()
        now_date = now.date()

        try:
            coin_limit = PlattformSettings.objects.get(id=1).coin_limit
        except PlattformSettings.DoesNotExist:
            coin_limit = 10000.00

        users = User.objects.all()
        users_to_update = []

        scheduled_credits = ScheduledCredit.objects.all()

        for scheduled_credit in scheduled_credits:
            if scheduled_credit.date < 0 or datetime.fromtimestamp(scheduled_credit.date, tz=pytz.UTC).date() == now_date:
                with transaction.atomic():
                    for user in users:
                        new_balance = user.coins + scheduled_credit.amount
                        user.coins = min(new_balance, coin_limit)
                        users_to_update.append(user)

                scheduled_credit.delete()

        if users_to_update:
            User.objects.bulk_update(users_to_update, ['coins'])
    finally:
            connection.close()

def process_platform_settings_recharge():
    from django.utils import timezone
    from datetime import timedelta
    from .models import PlattformSettings
    from user_api.models import User
    from django.db import transaction

    try:
        now = timezone.now()

        try:
            platform_settings = PlattformSettings.objects.get()
        except PlattformSettings.DoesNotExist:
            return

        coin_limit = platform_settings.coin_limit or 10000.00

        last = platform_settings.last_recharge or now
        interval = platform_settings.recharge_interval

        users = User.objects.all()
        users_to_update = []

        if interval == -1:
            with transaction.atomic():
                for user in users:
                    new_balance = user.coins + platform_settings.recharge_amount
                    user.coins = min(new_balance, coin_limit)
                    users_to_update.append(user)

            platform_settings.last_recharge = now
            platform_settings.recharge_interval = 30
            platform_settings.save()
        else:
            due_date = last + timedelta(days=interval)

            if now >= due_date:
                with transaction.atomic():
                    for user in users:
                        new_balance = user.coins + platform_settings.recharge_amount
                        user.coins = min(new_balance, coin_limit)
                        users_to_update.append(user)

                platform_settings.last_recharge = now
                platform_settings.save()

        if users_to_update:
            User.objects.bulk_update(users_to_update, ['coins'])

    finally:
        connection.close()

def ping(ip_address):
    try:
        response_time = ping_host(ip_address, timeout=1)
        return response_time is not None
    except Exception as e:
        print(f"[ERROR] Ping to {ip_address} failed: {e}")
        return False