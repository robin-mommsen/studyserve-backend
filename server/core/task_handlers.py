from logging import error
from django.db import connection
from core.mail_utils import send_server_login_data, send_service_data, send_server_deleted_mail, \
    send_service_deleted_mail

def handle_server_create_result(task):
    if task.success and task.result:
        try:
            server, ip_address, root_password, world_id = task.result
            server.status = "running"
            server.vps_status = "online"
            server.ip_address = str(ip_address)
            server.world_id = str(world_id)
            server.in_progress = False
            server.save()

            send_server_login_data(server.owner, server.hostname, ip_address, root_password)
        except Exception as e:
            error(f"Error handling task result: {e}")

    connection.close()

def handle_service_create_result(task):
    if task.success and task.result:
        try:
            service, ip_address, root_password, domain, world_id = task.result
            service.status = "running"
            service.vps_status = "online"
            service.ip_address = str(ip_address)
            service.world_id = str(world_id)
            service.domain = str(domain)
            service.in_progress = False
            service.save()

            send_service_data(service.owner, str(domain))
        except Exception as e:
            error(f"Error handling task result: {e}")

    connection.close()

def handle_server_delete_result(task):
    if task.success and task.result:
        try:
            server, reason = task.result
            server.is_deleted = True
            server.status = "shutdown"
            server.vps_status = "offline"
            server.save()

            send_server_deleted_mail(server.owner, server.hostname, reason)
        except Exception as e:
            error(f"Error handling task result: {e}")

    connection.close()

def handle_service_delete_result(task):
    if task.success and task.result:
        try:
            service, reason = task.result
            service.is_deleted = True
            service.status = "shutdown"
            service.vps_status = "offline"
            service.save()

            send_service_deleted_mail(service.owner, service.hostname, reason)
        except Exception as e:
            error(f"Error handling task result: {e}")
    else:
        error(f"Delete task failed: {task.id}, Error: {task.result}")

    connection.close()


def handle_server_action_result(task):
    if task.success and task.result:
        try:
            server, server_id, action = task.result

            if action == "start":
                server.status = "running"
                server.vps_status = "online"

            elif action == "stop":
                server.status = "stopped"
                server.vps_status = "offline"

            elif action == "shutdown":
                server.status = "shutdown"
                server.vps_status = "offline"

            server.in_progress = False
            server.save()

        except Exception as e:
            error(f"Error handling task result: {e}")

    else:
        error(f"Action-Task failed: {task.id}, Error: {task.result}")

    connection.close()

def handle_service_action_result(task):
    if task.success and task.result:
        try:
            service, service_id, action = task.result

            if action == "start":
                service.status = "running"
                service.vps_status = "online"

            elif action == "stop":
                service.status = "stopped"
                service.vps_status = "offline"

            elif action == "shutdown":
                service.status = "shutdown"
                service.vps_status = "offline"

            service.in_progress = False
            service.save()

        except Exception as e:
            error(f"Error handling task result: {e}")

    else:
        error(f"Action-Task failed: {task.id}, Error: {task.result}")

    connection.close()