import os
import argparse
import logging

from aiohttp import web

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='A simple file hosting HTTP server to pass verification for ZeroSSL')

parser.add_argument('file_path', help='The path to your authentication file, downloaded from ZeroSSL')

args = parser.parse_args()

content = str()
url = "/.well-known/pki-validation/"+os.path.basename(args.file_path)

with open(args.file_path, "r") as file:
    content = file.read()

async def auth_file(request):
    logging.info("Received GET request for auth file")
    return web.Response(text=content)

app = web.Application()
app.add_routes([web.get(url, auth_file)])
logging.info(f"Starting hosting of auth file under http://localhost{url}")
web.run_app(app, port=80)