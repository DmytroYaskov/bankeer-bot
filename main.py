

import os
import json
import logging

import asyncio
from aiohttp import web, ClientSession
import aiohttp

from datetime import datetime
from telegram import Bot
from telegram.ext import Application

from datetime import datetime

from db_commands import write_transactions_data
from record_processor import initial_data_preprocessing, hide_sensitive, mono_json_response

logging.basicConfig(level=logging.INFO)

BANK_TOKEN = os.environ["BANK_TOKEN"]
BANK_ACCOUNT_TOKEN = os.environ["BANK_ACCOUNT_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USERS = json.loads(os.environ["ALLOWED_USERS"])
CLIENT_SERVER_URL = os.environ["CLIENT_SERVER_URL"]

logging.info(f"BANK_TOKEN: {hide_sensitive(BANK_TOKEN)}")
logging.info(f"BANK_ACCOUNT_TOKEN: {hide_sensitive(BANK_ACCOUNT_TOKEN)}")
logging.info(f"TELEGRAM_BOT_TOKEN: {hide_sensitive(TELEGRAM_BOT_TOKEN)}")
logging.info(f"ALLOWED_USERS: { [hide_sensitive(user, 3) for user in ALLOWED_USERS] }")


# ============ client server for webhook [beg] ============
routes = web.RouteTableDef()

async def processing(data):
    if data["data"]["account"] == BANK_ACCOUNT_TOKEN:
        preprocessed_record = initial_data_preprocessing(data)
        mono_formatted_record = mono_json_response(preprocessed_record)
        await write_transactions_data(preprocessed_record)
        await send_tg(mono_formatted_record)
        logging.info("✅ Data was initially preprocessed written to DB")

@routes.get("/transactionData")
async def get_connection(request):
    return web.Response(text="Success", status=200)


@routes.post("/transactionData")
async def get_transaction_data(request):
    data = await request.json()

    loop = asyncio.get_event_loop()
    loop.create_task(processing(data))

    return web.Response(text="Success", status=200)


app = web.Application()
app.add_routes(routes)


async def run_app():
    # await web.run_app(app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    # asyncio.get_event_loop().run_forever()
    # await app

    await asyncio.sleep(99999)


async def enable_webhook(client_url):
    headers = {"X-Token": BANK_TOKEN}
    data = {"webHookUrl": client_url}
    async with ClientSession() as session:
        async with session.post(url="https://api.monobank.ua/personal/webhook", headers=headers, json=data) as response:
            return await response.text()


async def run_webhook():
    await asyncio.sleep(1)
    await enable_webhook(CLIENT_SERVER_URL)
    logging.info("✅ Webhook is now connected to the client server!")
# ============ client server for webhook [end] ============


async def send_tg(pretty_msg):

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    for user_id in ALLOWED_USERS:
        await application.bot.send_message(
            chat_id=user_id,
            text=pretty_msg
        )

    logging.info("✅ Sent message to users")

#     # last_checked_timestamp = datetime(2023, 1, 29, 0, 0, 0)

#     api_url=f"https://api.monobank.ua/personal/statement/{bank_account_token}/"

#     async with aiohttp.ClientSession(headers={"X-Token": bank_token}) as session:
#         while(True):

#             url = api_url+last_checked_timestamp.strftime('%s')

#             async with session.get(url=url) as resp:

#                 records = await resp.json()

#                 for record in records:
#                     if record["data"]["account"] == bank_account_token:
#                         preprocessed_record = initial_data_preprocessing(record)
#                         write_transactions_data(preprocessed_record)
#                         pretty_msg = mono_json_response(preprocessed_record)

#                         for user_id in allowed_users:
#                             await bot.send_message(
#                                 chat_id=user_id,
#                                 text=pretty_msg
#                             )

#             last_checked_timestamp = datetime.now()

#             await asyncio.sleep(60)

# async def main():

#     application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

#     async with application:

#         bank_check_loop_task = asyncio.create_task(
#             bank_check_loop(
#                 application.bot,
#                 ALLOWED_USERS,
#                 BANK_TOKEN,
#                 BANK_ACCOUNT_TOKEN
#             )
#         )

#         await application.start()

#         await asyncio.gather(
#             bank_check_loop_task
#         )


async def main():
    await asyncio.gather(
        run_app(),
        # app,
        run_webhook()
    )


if __name__ == '__main__':
    asyncio.run(main())
