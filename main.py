import os
import json
import logging
import asyncio

import iso18245 as MCC

from datetime       import datetime
from telegram.ext   import Application
from aiohttp        import web, ClientSession

def hide_sensitive(data, visible_symbols = 4):
    tmp_str = str(data)
    tmp_str = '*' * (len(tmp_str) - visible_symbols) + tmp_str[-visible_symbols:]
    return tmp_str

class WebhookServer:

    async def get_connection(self, request):
        logging.info("Received webhook confirmation request!")
        return web.Response(text="Success", status=200)

    async def post_transaction_data(self, request):
        data = await request.json()

        logging.info(data)

        asyncio.create_task(
            self.processing_callback(data)
        )

        return web.Response(text="Success", status=200)

    def __init__(self, processing_callback) -> None:

        self.processing_callback = processing_callback

        self.app = web.Application()
        # self.app.add_routes(self.routes)

        self.app.add_routes([web.get('/', self.get_connection),
                             web.post('/', self.post_transaction_data)])

        self.runner = web.AppRunner(self.app)

    async def start(self):
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, '0.0.0.0', 8080)

        await self.site.start()

class BankeerBot:

    def __init__(self):
        self.BANK_TOKEN = os.environ["BANK_TOKEN"]
        logging.info(f"BANK_TOKEN: {hide_sensitive(self.BANK_TOKEN)}")
        
        self.BANK_ACCOUNT_TOKEN = os.environ["BANK_ACCOUNT_TOKEN"]
        logging.info(f"BANK_ACCOUNT_TOKEN: {hide_sensitive(self.BANK_ACCOUNT_TOKEN)}")

        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
        logging.info(f"TELEGRAM_BOT_TOKEN: {hide_sensitive(TELEGRAM_BOT_TOKEN)}")

        self.ALLOWED_USERS = json.loads(os.environ["ALLOWED_USERS"])
        logging.info(f"ALLOWED_USERS: { [hide_sensitive(user, 3) for user in self.ALLOWED_USERS] }")

        self.PUBLIC_HOST_ADDRESS = os.environ["PUBLIC_HOST_ADDRESS"]
        logging.info(f"PUBLIC_HOST_ADDRESS: { [hide_sensitive(self.PUBLIC_HOST_ADDRESS)] }")
        
        self.chat_API = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        self.webhook_server = WebhookServer(self._processing)

    async def start(self):
        await self.chat_API.initialize()
        await self.chat_API.start()

        await self.webhook_server.start()

        await self._enable_webhook()

        logging.info("Bot started")
    
    async def _enable_webhook(self):
        url="https://api.monobank.ua/personal/webhook"
        headers = {"X-Token": self.BANK_TOKEN}
        data = {"webHookUrl": "https://"+self.PUBLIC_HOST_ADDRESS}

        async with ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
                return await response.text()
    
    async def _processing(self, data):
        if data["data"]["account"] == self.BANK_ACCOUNT_TOKEN:

            statement = data["data"]["statementItem"]

            logging.info(statement)

            record = self._gather_usefull_info(statement)

            formatted_record = self._format_json_response(record)

            for user_id in self.ALLOWED_USERS:
                await self.chat_API.bot.send_message(
                    chat_id=user_id,
                    text=formatted_record
                )
    
    @staticmethod
    def _gather_usefull_info(record={}):
        return {
            "time": datetime.fromtimestamp(record["time"]),
            "description": record["description"],
            "mcc": record["mcc"],
            "amount": record["amount"]/100.0,
            "balance": record["balance"]/100.0,
        }

    @staticmethod
    def _format_json_response(record):
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

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bankeer = BankeerBot()

    await bankeer.start()

    await asyncio.Event().wait()
    
if __name__ == '__main__':
    asyncio.run(main())