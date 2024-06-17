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
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.fileshare import ShareFileClient
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


def get_fileshare_client(fileshare_name: str, fileshare_path: str) -> ShareFileClient:
    """
    Creates a ShareFileClient to interact with a specific file in an Azure File Share.

    Args:
        fileshare_name (str): The name of the Azure File Share.
        fileshare_path (str): The path to the file within the Azure File Share.

    Returns:
        ShareFileClient: An instance of ShareFileClient for the specified file.
    """
    account_name = os.environ["FILESHARE_ACCOUNT"]
    account_key = os.environ["FILESHARE_KEY"]
    file_client = ShareFileClient(
        account_url=f"https://{account_name}.file.core.windows.net/",
        share_name=fileshare_name,
        file_path=fileshare_path,
        credential=account_key,
    )
    return file_client


def upload_to_fileshare(
    local_file_path: str, fileshare_name: str, fileshare_path: str
) -> None:
    """
    Uploads a local file to a specified path in an Azure File Share.

    Args:
        local_file_path (str): The local path of the file to upload.
        fileshare_name (str): The name of the Azure File Share.
        fileshare_path (str): The path within the Azure File Share where the file will be uploaded.

    Returns:
        None
    """
    file_client = get_fileshare_client(
        fileshare_name=fileshare_name, fileshare_path=fileshare_path
    )
    with open(local_file_path, "rb") as source_file:
        file_client.upload_file(source_file)


def download_from_fileshare(
    local_file_path: str, fileshare_name: str, fileshare_path: str
) -> None:
    """
    Downloads a file from a specified path in an Azure File Share to a local path.

    Args:
        local_file_path (str): The local path where the file will be saved.
        fileshare_name (str): The name of the Azure File Share.
        fileshare_path (str): The path within the Azure File Share from where the file will be downloaded.

    Returns:
        None
    """
    file_client = get_fileshare_client(
        fileshare_name=fileshare_name, fileshare_path=fileshare_path
    )
    with open(local_file_path, "wb") as target_file:
        data = file_client.download_file()
        data.readinto(target_file)
