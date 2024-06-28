# pylint: disable=line-too-long
# pylint: disable=missing-timeout
"""
Power BI Export Module

This module provides functions to interact with the Power BI API for exporting reports and pages to various formats,
such as PowerPoint (PPTX). It includes functions for authentication, listing pages, and exporting specific pages
with optional filters.

Functions:
- get_access_token(instance: ReportInstance) -> str:
    Authenticates with Azure AD using client credentials and retrieves an access token for Power BI API.

- list_pages(instance: ReportInstance, token: str) -> Dict[str, Any]:
    Retrieves a list of pages from a Power BI report using the specified instance and authorization token.

- async get_report_page(session, instance: ReportInstance, token: str, page_config: ReportPageConfig, ppt_file_name: str) -> None:
    Asynchronously exports a specific page of a Power BI report to a PowerPoint (PPTX) file with optional filters.
    Uses an aiohttp ClientSession for asynchronous HTTP requests.

- async get_all_pages(report_config: List[ReportPageConfig], instance: ReportInstance, token: str, ppt_id: str):
    Asynchronously exports all pages from a list of ReportPageConfig instances to PowerPoint (PPTX) files.
    Divides the export process into chunks of 25 pages to manage API rate limits and pauses for 1 minute between chunks.

Dependencies:
- requests: For making synchronous HTTP requests.
- aiohttp: For making asynchronous HTTP requests.
- namedtuple: To define the ReportInstance tuple for encapsulating Power BI report instance details.
- src.config.ReportPageConfig: Custom module defining ReportPageConfig class for page configurations.
- src.pbiexc.PBIExportError: Custom exception class for handling Power BI export errors.
"""

import asyncio
from typing import Dict, Any, List
from collections import namedtuple
import requests
import aiohttp
from config import ReportPageConfig  # pylint: disable=import-error
from exc import PBIExportError  # pylint: disable=import-error

SCOPE = "https://analysis.windows.net/powerbi/api/.default"
ReportInstance = namedtuple(
    "ReportInstance",
    ["client_id", "client_secret", "tenant_id", "workspace_id", "report_id"],
)


def get_access_token(instance: ReportInstance) -> str:
    """
    Authenticate with Azure AD and retrieve an access token.

    Args:
    - instance (ReportInstance): The ReportInstance containing client_id, client_secret, and tenant_id.

    Returns:
    - str: The access token.
    """

    params = {
        "grant_type": "client_credentials",
        "client_id": instance.client_id,
        "client_secret": instance.client_secret,
        "scope": SCOPE,
    }
    tenant_id = instance.tenant_id
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    r = requests.post(auth_url, data=params)
    r.raise_for_status()  # Raise an exception for HTTP errors
    token = r.json()["access_token"]
    return token


def list_pages(instance: ReportInstance, token: str) -> Dict[str, Any]:  #
    """
    Retrieve a list of pages from a Power BI report.

    Args:
    - instance (ReportInstance): The ReportInstance containing workspace_id and report_id.
    - token (str): The authorization token.

    Returns:
    - Dict[str, Any]: A dictionary containing the page data.
    """
    workspace_id = instance.workspace_id
    report_id = instance.report_id
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/pages"
    headers = {
        "Authorization": f"Bearer {token}",  # Ensure token is formatted correctly
        "Content-Type": "application/json",
    }

    # Send the GET request
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    page_data = response.json()
    return page_data


async def get_report_page(
    session,
    instance: ReportInstance,
    token: str,
    page_config: ReportPageConfig,
    ppt_file_name: str,
) -> None:
    """
    Export a specific page of a Power BI report to a PDF file with optional filters.

    Args:
    - session (ClientSession): The aiohttp session to use for requests.
    - instance (ReportInstance): The ReportInstance containing workspace_id and report_id.
    - token (str): The authorization token.
    - page_config (ReportPageConfig): The page configuration containing pageName and optional measureId.
    - ppt_file_name (str): The name of the file to save the exported PowerPoint file as.

    Returns:
    - None: The function saves the exported PowerPoint file to a file.
    """
    workspace_id = instance.workspace_id
    report_id = instance.report_id
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/ExportTo"

    if page_config.measureId:
        if page_config.comparativeMeasureId:
            # TODO: confirm this
            # filter_string=f"scd_Measure/Measure_ID in ('{page_config.measureId}') and scd_Measure/Comparative_Measure_ID in ('{page_config.comparativeMeasureId}')"
            filter_string = f"scd_Measure/Measure_ID in ('{page_config.measureId}')"
        else:
            filter_string = f"scd_Measure/Measure_ID in ('{page_config.measureId}')"

        data = {
            "format": "PPTX",
            "powerBIReportConfiguration": {
                "pages": [{"pageName": page_config.pageName}],
                "reportLevelFilters": [{"filter": filter_string}],
            },
        }
    else:
        data = {
            "format": "PPTX",
            "powerBIReportConfiguration": {
                "pages": [{"pageName": page_config.pageName}]
            },
        }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    async with session.post(url, json=data, headers=headers) as response:  #
        try:
            response.raise_for_status()
            if response.status == 202:
                export_id = (await response.json())["id"]
                status_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/exports/{export_id}"
                export_completed = False
                while not export_completed:
                    async with session.get(
                        status_url, headers=headers
                    ) as status_response:

                        status_response.raise_for_status()
                        status_data = await status_response.json()
                        if status_data["status"] == "Succeeded":
                            export_completed = True
                            file_url = status_data["resourceLocation"]
                        elif status_data["status"] == "Failed":
                            raise PBIExportError(
                                f"Export failed: {status_data['error']['message']}"
                            )
                        else:
                            await asyncio.sleep(5)
                async with session.get(file_url, headers=headers) as file_response:
                    file_response.raise_for_status()
                    with open(ppt_file_name, "wb") as file:
                        file.write(await file_response.read())
                print(
                    f"Requesting {page_config.pageName} with {page_config.displayName} successful!!"
                )
        except Exception as e:
            print(
                f"Requesting {page_config.pageName} with {page_config.displayName} failed"
            )
            raise e


async def get_all_pages(
    report_config: List[ReportPageConfig],
    instance: ReportInstance,
    token: str,
    ppt_id: str,
    chunk_size: int = 5,
):
    """
    Export all pages from a list of ReportPageConfig asynchronously.

    Args:
    - report_config (List[ReportPageConfig]): List of ReportPageConfig instances containing page configurations.
    - instance (ReportInstance): The ReportInstance containing workspace_id and report_id.
    - token (str): The authorization token.
    - ppt_id (str): ID for the PowerPoint file.
    - chunk_size (int): Number of requests to make at the same time

    Returns:
    - None: The function asynchronously exports all pages to PowerPoint files.
    """
    report_len = len(report_config)
    chunk_size = min(report_len, chunk_size)

    async with aiohttp.ClientSession() as session:
        for i in range(0, report_len, chunk_size):
            chunk = report_config[i : i + chunk_size]
            tasks = []

            for page in chunk:
                ppt_file_name = f"{ppt_id}/Page {str(page.pageOrder).zfill(2)}.pptx"
                task = asyncio.create_task(
                    get_report_page(
                        session=session,
                        instance=instance,
                        token=token,
                        page_config=page,
                        ppt_file_name=ppt_file_name,
                    )
                )
                tasks.append(task)

            await asyncio.gather(*tasks)
