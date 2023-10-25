from amazon_services.amazon_manager import AmazonManager
from config import SELLER_CENTRAL_CONFIG
from download_report import download_fba_inv

from email_helper import send_email
import traceback
from time import sleep
import pandas as pd
from util import get_file_path

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


import datetime


def dataframe_to_gsheet(df, spreadsheet_name, worksheet_name):
    # Setup the Google Sheets API credentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and worksheet
    spreadsheet = client.open(spreadsheet_name)

    # Try to access the worksheet. If it doesn't exist, create one.
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows="100", cols="100"
        )

    # Prepare data for update
    # Create a timestamp row
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_row = ["Last updated:", current_time] + [""] * (len(df.columns) - 2)

    # Combine the timestamp, header row, and dataframe values
    data_to_upload = [timestamp_row, df.columns.values.tolist()] + df.values.tolist()

    # Update the worksheet
    worksheet.update(data_to_upload)


# Usage:


def main():
    try:
        seller_central = AmazonManager(
            SELLER_CENTRAL_CONFIG["amazon_login"]["username"],
            SELLER_CENTRAL_CONFIG["amazon_login"]["password"],
            SELLER_CENTRAL_CONFIG["amazon_links"]["login_link"],
            SELLER_CENTRAL_CONFIG["amazon_xpaths"],
            SELLER_CENTRAL_CONFIG["gmail_config"]["sender_email"],
            SELLER_CENTRAL_CONFIG["gmail_config"]["recipient_emails"],
            SELLER_CENTRAL_CONFIG["type"],
        )
        seller_central.login()
        REPORT_FBA_INV = " https://sellercentral.amazon.com/reportcentral/FBA_MYI_UNSUPPRESSED_INVENTORY/1"
        download_fba_inv(seller_central, REPORT_FBA_INV)

        sleep(5)
        # df = pd.read_csv(get_file_path(seller_central.driver_actions.download_path))
        download_folder_path = seller_central.driver_actions.download_path
        seller_central.driver_actions.quit()
        df = pd.read_csv(get_file_path(download_folder_path), encoding="ISO-8859-1")
        df["usable-sku"] = (
            df["sku"]
            .str.replace("-FBA", "", regex=False)
            .str.replace("_FBA", "", regex=False)
        )

        df.fillna(
            0, inplace=True
        )  # Replace NaN with "N/A" or another placeholder value
        spreadsheet_name = "Inventory Forecast Algorithm"
        worksheet_name = "FBA Inventory"
        dataframe_to_gsheet(df, spreadsheet_name, worksheet_name)

        # process_order_removal_detail(seller_central)
        # process_removal_shipment_detail(seller_central)
    except Exception as e:
        # If an error occurs, send an email with the traceback
        send_email("Error Updating Inventory", traceback.format_exc())


if __name__ == "__main__":
    main()
