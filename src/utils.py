# pylint: disable=line-too-long
"""
Utility Module

This module provides utility functions for email operations including sending emails with attachments,
generating random IDs, creating directories, and retrieving credentials from a key vault (not implemented).

Functions:
- get_credential(name: str) -> str:
    Retrieves a credential from a key vault (not implemented).

- make_dir(directory_path: str) -> None:
    Creates a directory if it doesn't already exist.

- generate_id(length: int = 8) -> str:
    Generates a random ID of the specified length using alphanumeric characters.

- send_email(emails: list, subject: str, message: str, attachment: str = None) -> None:
    Sends an email with optional attachment(s) to specified email addresses using SMTP.

Dependencies:
- os: For filesystem operations like directory creation.
- string: For generating random IDs using alphanumeric characters.
- random: For randomizing characters in generating random IDs.
- smtplib: For sending emails via SMTP.
- email.mime.multipart.MIMEMultipart: For constructing multipart emails.
- email.mime.text.MIMEText: For constructing email text content.
- email.mime.application.MIMEApplication: For constructing email attachments.

Note:
- The get_credential function is currently a placeholder and raises a NotImplementedError.
- The send_email function requires email credentials (inbox, password, server host, server port, sender name).
"""

import os
import string
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from exc import KeyVaultError  # pylint: disable=import-error


def get_credential(name: str) -> str:
    """
    Retrieves a credential value from Azure KeyVault

    Parameters:
    name (str): The name of the credential inside KeyVault

    Returns:
    - credential (str)

    Raises:
    - KeyVaultError: If credential is not found or is empty
    """
    kv_uri = "https://qvh-keyvault.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)
    credential_value = client.get_secret(name).value
    if not credential_value:
        raise KeyVaultError("Credential value not found, please check KeyVault")
    return credential_value


def make_dir(directory_path):
    """
    Creates a directory if it doesn't already exist.

    Parameters:
    - directory_path (str): The path of the directory to create.

    Returns:
    - None
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory {directory_path} created.")
    else:
        print(f"Directory {directory_path} already exists.")


def generate_id(length: int = 8) -> str:
    """
    Generates a random ID of the specified length.

    Parameters:
    - length (int): The length of the random ID to generate. Default is 8.

    Returns:
    - str: The generated random ID.
    """
    characters = string.ascii_letters + string.digits
    random_id = "".join(random.choice(characters) for _ in range(length))
    return random_id


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
