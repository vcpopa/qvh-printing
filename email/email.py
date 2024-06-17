import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reporting.utils import get_credential
def send_email(emails, subject, message, attachment=None):
    """
    Sends an email with optional attachment(s) to specified email addresses using SMTP.

    Args:
    - emails (list): List of email addresses to send the email to.
    - subject (str): Subject line of the email.
    - message (str): HTML content of the email body.
    - attachment (str, optional): File path of the attachment. Default is None.

    Returns:
    - None

    Notes:
    - Requires credentials from the key vault (not implemented) for email inbox, password, server host, server port, and sender name.
    """
    email_inbox = get_credential("email-address")
    email_pwd = get_credential("email-password")
    emailfrom = email_inbox
    email_server_host = get_credential("email-server-host")
    email_server_port = int(get_credential("email-server-port"))
    namefrom = get_credential("email-name-from")

    for emailto in emails:
        msg = MIMEMultipart()
        msg["From"] = f"{namefrom} <{emailfrom}>"
        msg["To"] = emailto
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "html"))

        if attachment:
            with open(attachment, "rb") as file:
                attach = MIMEApplication(file.read(), _subtype="txt")
                attach.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=attachment.replace("logs", ""),
                )
                msg.attach(attach)

        server = smtplib.SMTP(email_server_host, email_server_port)
        server.starttls()
        server.login(email_inbox, email_pwd)
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()