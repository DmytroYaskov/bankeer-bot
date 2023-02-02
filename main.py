import os
import json
import logging
import asyncio

from telegram import Bot
from telegram.ext import Application

def hide_sensitive(data, visible_symbols = 4):
    tmp_str = str(data)
    tmp_str = '*' * (len(tmp_str) - visible_symbols) + tmp_str[-visible_symbols:]
    return tmp_str

async def bank_check_loop(bot: Bot, users):
    while(True):

        for user_id in users:
            await bot.send_message(chat_id=user_id, text="HI!")
            
        await asyncio.sleep(60)

async def main():
    logging.basicConfig(level=logging.INFO)

    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    logging.info(f"TELEGRAM_BOT_TOKEN: {hide_sensitive(TELEGRAM_BOT_TOKEN)}")

    users = json.loads(os.environ["USERLIST"])
    logging.info(f"User: { [hide_sensitive(user, 3) for user in users] }")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async with application:

        bank_check_loop_task = asyncio.create_task(bank_check_loop(application.bot, users))

        await application.start()

        await asyncio.gather(
            bank_check_loop_task
        )
    
if __name__ == '__main__':
    asyncio.run(main())