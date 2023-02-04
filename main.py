import os
import json
import logging
import asyncio
import aiohttp

import iso18245 as MCC

from datetime       import datetime
from telegram       import Bot
from telegram.ext   import Application

def hide_sensitive(data, visible_symbols = 4):
    tmp_str = str(data)
    tmp_str = '*' * (len(tmp_str) - visible_symbols) + tmp_str[-visible_symbols:]
    return tmp_str

def gather_usefull_info(record={}):
    return {
        "time": datetime.fromtimestamp(record["time"]),
        "description": record["description"],
        "mcc": record["mcc"],
        "amount": record["amount"]/100.0,
        "balance": record["balance"]/100.0,
    }

def format_json_response(record):

    transaction_type = "⬇️ Поповнення на" if record["amount"] > 0 else "⬆️ Списання"

    mcc_desc = MCC.get_mcc(str(record['mcc'])).usda_description

    description = record['description'].replace('\n', ' ')

    return (
        f"📆 {record['time']}\n"
        f"{transaction_type}: {record['amount']} UAH\n"
        f"💰 Поточний баланс: {record['balance']} UAH\n"
        f"🏢 {mcc_desc}\n" #  
        f"📃 Опис: {description}"
    )
    

async def bank_check_loop(bot: Bot, allowed_users, bank_token, bank_account_token):

    last_checked_timestamp = datetime(2023, 1, 29, 0, 0, 0)
    
    api_url=f"https://api.monobank.ua/personal/statement/{bank_account_token}/"

    async with aiohttp.ClientSession(headers={"X-Token": bank_token}) as session:
        while(True):

            url = api_url+last_checked_timestamp.strftime('%s')

            async with session.get(url=url) as resp:

                records = await resp.json()

                for record in reversed(records):
                    parsed_record = gather_usefull_info(record)
                    pretty_msg = format_json_response(parsed_record)
            
                    for user_id in allowed_users:
                        await bot.send_message(
                            chat_id=user_id,
                            text=pretty_msg
                        )

            last_checked_timestamp = datetime.now()

            await asyncio.sleep(60)

async def main():
    logging.basicConfig(level=logging.INFO)

    BANK_TOKEN = os.environ["BANK_TOKEN"]
    logging.info(f"BANK_TOKEN: {hide_sensitive(BANK_TOKEN)}")
    
    BANK_ACCOUNT_TOKEN = os.environ["BANK_ACCOUNT_TOKEN"]
    logging.info(f"BANK_ACCOUNT_TOKEN: {hide_sensitive(BANK_ACCOUNT_TOKEN)}")

    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    logging.info(f"TELEGRAM_BOT_TOKEN: {hide_sensitive(TELEGRAM_BOT_TOKEN)}")

    ALLOWED_USERS = json.loads(os.environ["ALLOWED_USERS"])
    logging.info(f"ALLOWED_USERS: { [hide_sensitive(user, 3) for user in ALLOWED_USERS] }")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async with application:

        bank_check_loop_task = asyncio.create_task(
            bank_check_loop(
                application.bot,
                ALLOWED_USERS,
                BANK_TOKEN,
                BANK_ACCOUNT_TOKEN
                )
        )

        await application.start()

        await asyncio.gather(
            bank_check_loop_task
        )
    
if __name__ == '__main__':
    asyncio.run(main())