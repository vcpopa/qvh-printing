"""
This script processes Power BI reports and sends email notifications with the generated presentations.

Usage:
    python main.py --measure <measure> --emails <email1> <email2> ... --azure_client_id <client_id> --azure_client_secret <client_secret> --azure_tenant_id <tenant_id> [--chunk_size <chunk_size>]

Arguments:
    --measure            The measure to filter pages by (e.g., KS01, KS02, KS03, KS04, KS05, all).
    --emails             List of email addresses to send notifications to.
    --azure_client_id    The Azure client ID.
    --azure_client_secret The Azure client secret.
    --azure_tenant_id    The Azure tenant ID.
    --chunk_size         Chunk size for processing (optional, default: 5).

The script loads the report configuration, retrieves the Power BI report pages, merges them into a single presentation, and sends the presentation via email.
"""

import argparse
import os
import asyncio
from utils import (
    generate_id,
    make_dir,
    upload_to_fileshare,
)
from pbi import (
    get_access_token,
    get_all_pages,
    ReportInstance,
)
from config import load_report_config
from ppt import merge_presentations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--chunk_size", type=int, default=5, help="Chunk size (default: 5)"
    )
    args = parser.parse_args()
    chunk_size = args.chunk_size
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    tenant_id = os.environ["AZURE_TENANT_ID"]
    workspace_id = os.environ["WORKSPACE_ID"]
    report_id = os.environ["REPORT_ID"]
    environment = os.environ['ENVIRONMENT']
    page_name = os.environ['PAGE']
    if environment not in  ['DEV','PROD']:
        raise EnvironmentError("Environment must be one of DEV or PROD")

    report_instance = ReportInstance(
        client_id, client_secret, tenant_id, workspace_id, report_id
    )
    token = get_access_token(report_instance)
    report_config = load_report_config(page_name=page_name)
    run_id = generate_id()
    make_dir(run_id)
    asyncio.run(
        get_all_pages(
            report_config=report_config,
            instance=report_instance,
            token=token,
            ppt_id=run_id,
            chunk_size=chunk_size,
        )
    )
    if environment == 'DEV':
        report_name=f"DEV_{page_name}.pptx"
    else:
        report_name = f"{page_name}.pptx"

    merge_presentations(
        directory_path=run_id, output_filename=f"{run_id}/{report_name}"
    )
    upload_to_fileshare(
        local_file_path=f"{run_id}/{report_name}",
        fileshare_path=f"Reports/{report_name}",
        fileshare_name="qvh",
    )
