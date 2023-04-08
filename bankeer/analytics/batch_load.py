import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
                )
sys.path.append(PROJECT_ROOT)

from datetime import date
import datetime
import requests
import asyncio
import logging
import time


import db

logging.basicConfig(level=logging.INFO)


def get_month_delta_timestamp(last_date):
    one_month = last_date - datetime.timedelta(days=30)
    unix_timestamp = one_month.strftime('%s')
    return unix_timestamp


def batch_load_transactions(token, account):
    headers = {"X-Token": token}
    start_date = get_month_delta_timestamp(date.today())
    response = requests.get(
        url=f"https://api.monobank.ua/personal/statement/{account}/{start_date}", headers=headers).json()
    if "errorDescription" in response:
        time.sleep(60)
        response = requests.get(
            url=f"https://api.monobank.ua/personal/statement/{account}/{start_date}", headers=headers).json()
    return response


async def write_batch():
    BANK_TOKEN = os.environ["BANK_TOKEN"]
    BANK_ACCOUNT_TOKEN = os.environ["BANK_ACCOUNT_TOKEN"]
    DB_NAME = os.environ["DATABASE_NAME"]
    MAIN_TABLE_NAME = os.environ["MAIN_TABLE_NAME"]
    MCC_TABLE_NAME = os.environ["MCC_TABLE_NAME"]

    db_manager = db.DatabaseManager(DB_NAME, MAIN_TABLE_NAME, MCC_TABLE_NAME)

    transaction_list = batch_load_transactions(BANK_TOKEN, BANK_ACCOUNT_TOKEN)
    # print(transaction_list)
    import iso18245 as MCC
    # mcc_text = dir(MCC.get_mcc(str("9403")).mcc)
    # print(mcc_text)


    # total_no_changes = 0
    for transaction in transaction_list:
        mcc_descr = MCC.get_mcc(str(transaction["mcc"])).range.description
        mcc_text = MCC.get_mcc(str(transaction["mcc"])).iso_description

        print(transaction["mcc"], transaction["originalMcc"], transaction["amount"] / 100, mcc_text, mcc_descr)
        # preprocessed = initial_data_preprocessing(transaction, batch=True)
    #     no_changes = await db_manager.write_transactions_data(preprocessed, BANK_ACCOUNT_TOKEN)
    #     total_no_changes += no_changes
    # logging.info(f"Total number of changes made to DB: {total_no_changes}")


if __name__ == '__main__':
    asyncio.run(write_batch())




