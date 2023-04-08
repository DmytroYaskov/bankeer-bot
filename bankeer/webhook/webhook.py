import logging
import asyncio

from aiohttp import web


class WebhookServer:
    def __init__(self, processing_callback) -> None:

        self.processing_callback = processing_callback

        self.app = web.Application()
        # self.app.add_routes(self.routes)

        self.app.add_routes([web.get('/', self.get_connection),
                             web.post('/', self.post_transaction_data)])

        self.runner = web.AppRunner(self.app)

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


    async def start(self):
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, '0.0.0.0', 8080)

        await self.site.start()

    