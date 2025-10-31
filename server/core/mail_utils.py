from mailer import send_mail

def send_server_login_data(user, hostname, ip_address, root_password):
    username = user.username
    email = user.email

    subject = f"Dein Server ist jetzt aktiv, {username}!"
    message = (
        f"Hallo {username},\n\n"
        f"dein Server **{hostname}** wurde erfolgreich erstellt und ist jetzt unter folgender IP-Adresse erreichbar:\n"
        f"{ip_address}\n\n"
        f"Du kannst dich mit den folgenden Zugangsdaten anmelden:\n"
        f"Benutzername: `root`\n"
        f"Passwort: `{root_password}` *(bitte nach dem ersten Login ändern!)*\n\n"
        f"Viel Spaß beim Entwickeln!\n"
    )

    try:
        send_mail(subject, message,None, [email])
    except Exception as e:
        print(f"Mail error: {e}")


def send_service_data(user, domain):
    username = user.username
    email = user.email

    subject = f"Dein Dienst ist jetzt aktiv, {username}!"
    message = (
        f"Hallo {username},\n\n"
        f"dein Dienst wurde erfolgreich erstellt und ist jetzt unter folgender Domain erreichbar:\n"
        f"{domain}\n\n"
        f"Viel Spaß beim Entwickeln!\n"
    )

    try:
        send_mail(subject, message,None, [email])
    except Exception as e:
        print(f"Mail error: {e}")

def send_server_expiry_warning_email(server, expiry_date, days_left):
    user = server.owner

    subject = f"Dein Server '{server.hostname}' läuft in {days_left} Tag(en) ab"
    message = (
        f"Hallo {user.username},\n\n"
        f"dies ist eine Erinnerung, dass dein Server **'{server.hostname}'** in {days_left} Tag(en), "
        f"am {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}, abläuft.\n\n"
        f"Bitte lade rechtzeitig Guthaben auf, ansonsten wird der Server unwiderruflich gelöscht.\n\n"
        f"Viele Grüße,\n"
        f"Dein Server-Team"
    )

    try:
        send_mail(subject, message, None, [user.email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")


def send_service_expiry_warning_email(service, expiry_date, days_left):
    user = service.owner

    subject = f"Dein Dienst '{service.hostname}' läuft in {days_left} Tag(en) ab"
    message = (
        f"Hallo {user.username},\n\n"
        f"dies ist eine Erinnerung, dass dein Dienst **'{service.hostname}'** in {days_left} Tag(en), "
        f"am {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}, abläuft.\n\n"
        f"Bitte lade rechtzeitig Guthaben auf, ansonsten wird der Dienst unwiderruflich gelöscht.\n\n"
        f"Viele Grüße,\n"
        f"Dein Server-Team"
    )

    try:
        send_mail(subject, message, None, [user.email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")


def send_expiry_warning_email_without_timestamp(user, servers, services):
    subject = f"Warnung: Deine Server und Dienste laufen bald ab"
    message = f"Hallo {user.username},\n\n"
    message += "die folgenden Server und Dienste ohne Ablaufdatum können nur noch für die angegebene Anzahl an Tagen bezahlt werden:\n\n"

    if servers:
        message += "Server:\n"
        for server, days_left in servers:
            message += f"- {server.hostname}: {days_left} Tag(e) verbleibend\n"

    if services:
        message += "\nDienste:\n"
        for service, days_left in services:
            message += f"- {service.hostname}: {days_left} Tag(e) verbleibend\n"

    message += (
        "\nBitte lade rechtzeitig Guthaben auf, ansonsten werden die Server und Dienste unwiderruflich gelöscht.\n\n"
        "Viele Grüße,\n"
        "Dein Server-Team"
    )

    try:
        send_mail(subject, message, None, [user.email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")


def send_invitation_mail(invited_user, project):
    project_name = project.name

    subject = f"Du wurdest zu dem Projekt '{project_name}' eingeladen!"
    message = (
        f"Hallo {invited_user.username},\n\n"
        f"du wurdest von {project.owner.username} zu dem Projekt **'{project_name}'** eingeladen.\n\n"
        f"Wenn du beitreten möchtest, klicke bitte auf den folgenden Link, um die Einladung zu akzeptieren:\n"
        f"Link zur Einladung: https://webapp.studyserve.de/invitation/accept?project={project.id}\n\n"
        f"Viel Spaß beim Mitwirken an diesem Projekt!\n"
    )

    try:
        send_mail(subject, message, None, [invited_user.email])
    except Exception as e:
        print(f"Fehler beim Senden der Einladung zu Projekt '{project_name}' an {invited_user.email}: {e}")

def send_invitation_accepted_mail(inviter, invited_user, project):
    subject = f"{invited_user.username} hat deine Projekteinladung angenommen!"
    message = (
        f"Hallo {inviter.username},\n\n"
        f"{invited_user.username} hat deine Einladung für das Projekt '{project.name}' angenommen.\n\n"
        f"Du kannst den aktuellen Stand unter deinem Projekt-Dashboard einsehen.\n\n"
        f"Viele Grüße,\n"
        f"Dein Server-Team"
    )

    try:
        send_mail(subject, message, None, [inviter.email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")

def send_invitation_declined_mail(inviter, invited_user, project):
    subject = f"{invited_user.username} hat deine Projekteinladung abgelehnt!"
    message = (
        f"Hallo {inviter.username},\n\n"
        f"{invited_user.username} hat deine Einladung für das Projekt '{project.name}' abgelehnt.\n\n"
        f"Du kannst den aktuellen Stand unter deinem Projekt-Dashboard einsehen.\n\n"
        f"Viele Grüße,\n"
        f"Dein Server-Team"
    )

    try:
        send_mail(subject, message, None, [inviter.email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")

def send_server_deleted_mail(user, hostname, reason):
    username = user.username
    email = user.email

    subject = "Dein Server wurde gelöscht"

    if reason == "insufficient_funds":
        message = (
            f"Hallo {username},\n\n"
            f"leider mussten wir deinen Server **{hostname}** löschen, da dein Guthaben nicht mehr ausgereicht hat, um den Betrieb aufrechtzuerhalten.\n\n "
            f"Da du auf unsere drei vorherigen Benachrichtigungen nicht reagiert hast, wurde der Server nun endgültig gelöscht.\n\n"
            f"Sobald du wieder Guthaben hast, kannst du selbstverständlich jederzeit einen neuen Server bei uns erstellen.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    elif reason == "deleted_by_admin":
        message = (
            f"Hallo {username},\n\n"
            f"dein Server **{hostname}** wurde von einem Administrator gelöscht. \n\n"
            f"Wenn du Fragen dazu hast oder glaubst, dass es sich um ein Missverständnis handelt, wende dich bitte an unseren Support.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    elif reason == "deleted_by_owner":
        message = (
            f"Hallo {username},\n\n"
            f"du hast deinen Server **{hostname}** erfolgreich gelöscht.\n\n"
            f"Wenn du in Zukunft wieder einen Server benötigst, kannst du jederzeit einen neuen bei uns erstellen.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    else:
        message = (
            f"Hallo {username},\n\n"
            f"dein Server **{hostname}** wurde gelöscht.\n\n Grund: {reason}\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )

    try:
        send_mail(subject, message, None, [email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")


def send_service_deleted_mail(user, hostname, reason):
    username = user.username
    email = user.email

    subject = "Dein Dienst wurde gelöscht"

    if reason == "insufficient_funds":
        message = (
            f"Hallo {username},\n\n"
            f"leider mussten wir deinen Dienst **{hostname}** löschen, da dein Guthaben nicht mehr ausgereicht hat, um den Betrieb aufrechtzuerhalten.\n\n "
            f"Da du auf unsere drei vorherigen Benachrichtigungen nicht reagiert hast, wurde der Dienst nun endgültig gelöscht.\n\n"
            f"Sobald du wieder Guthaben hast, kannst du selbstverständlich jederzeit einen neuen Dienst bei uns erstellen.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    elif reason == "deleted_by_admin":
        message = (
            f"Hallo {username},\n\n"
            f"dein Dienst **{hostname}** wurde von einem Administrator gelöscht. \n\n"
            f"Wenn du Fragen dazu hast oder glaubst, dass es sich um ein Missverständnis handelt, wende dich bitte an unseren Support.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    elif reason == "deleted_by_owner":
        message = (
            f"Hallo {username},\n\n"
            f"du hast deinen Dienst **{hostname}** erfolgreich gelöscht.\n\n"
            f"Wenn du in Zukunft wieder einen Dienst benötigst, kannst du jederzeit einen neuen bei uns erstellen.\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )
    else:
        message = (
            f"Hallo {username},\n\n"
            f"dein Dienst **{hostname}** wurde gelöscht.\n\n Grund: {reason}\n\n"
            f"Viele Grüße\n"
            f"Dein Server-Team"
        )

    try:
        send_mail(subject, message, None, [email])
    except Exception as e:
        print(f"MAIL ERROR: {e}")
