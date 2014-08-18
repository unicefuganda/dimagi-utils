from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives


def send_HTML_email(subject, recipient, text_content, html_content):

    # If you get the return_path header wrong, this may impede mail delivery. It appears that the SMTP server
    # has to recognize the return_path as being valid for the sending host. If we set it to, say, our SMTP
    # server, this will always be the case (as the server is explicitly serving the host).
    email_return_path = getattr(settings, 'EMAIL_RETURN_PATH', None)
    if email_return_path is None:
        # Get last two parts of the SMTP server as a proxy for the domain name from which this mail is sent.
        # This works for gmail, anyway.
        email_return_path = settings.EMAIL_LOGIN

    email_from = getattr(settings, 'EMAIL_FROM', None)
    if email_from is None:
        email_from = email_return_path
    from_header = {'From': email_from}  # From-header
    connection = get_connection()

    msg = EmailMultiAlternatives(subject, text_content, email_return_path, [recipient], headers=from_header, connection=connection)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
