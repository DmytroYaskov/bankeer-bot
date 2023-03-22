from datetime import date
import datetime
import requests
import pprint
import os

from record_processor import initial_data_preprocessing
from db_commands import write_transactions_data

def get_month_delta_timestamp(last_date):
    one_month = last_date - datetime.timedelta(days=31)
    unix_timestamp = one_month.strftime('%s')
    return unix_timestamp

def batch_load_transactions(token, account):
    headers = {"X-Token": token}
    start_date = get_month_delta_timestamp(date.today())
    response = requests.get(url=f"https://api.monobank.ua/personal/statement/{account}/{start_date}", headers=headers)
    return response

async def main():
    BANK_TOKEN = os.environ["BANK_TOKEN"]
    BANK_ACCOUNT_TOKEN = os.environ["BANK_ACCOUNT_TOKEN"]

    transaction_list = batch_load_transactions(BANK_TOKEN, BANK_ACCOUNT_TOKEN)

    for transaction in transaction_list:
        preprocessed = initial_data_preprocessing(transaction, batch=True)
        await write_transactions_data(preprocessed)

