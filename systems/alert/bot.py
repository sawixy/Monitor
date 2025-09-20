from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

import os

dp = Dispatcher()

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Bot started")

@dp.message(Command("add"))
async def add(msg: Message):
    args = msg.text.split()[1:]
    
    if not args:
        await msg.answer("Expected URL")
        return
    
    url = args[0]
    alias = None
    provider = "scrapfly"
    
    for arg in args[1:]:
        if arg.startswith('provider='):
            provider = arg.split('=', 1)[1].lower()
        elif arg.startswith('alias='):
            alias = arg.split('=', 1)[1]
        else:
            alias = arg
    
    if not alias:
        await msg.answer("Incorrect alias")
        return

    if provider not in ['scrapfly', 'scraper', 'hexowatch']:
        await msg.answer("Incorrect provider")
        return
    
    await msg.answer(f"Added: {url} (alias: {alias}, provider: {provider})")

@dp.message(Command("remove"))
async def remove(msg: Message):
    args = msg.text.split()[1:]
    
    if not args:
        await msg.answer("Incorrect alias")
        return
    
    target = args[0]
    
    if is_valid_url(target):
        await msg.answer(f"Deleted url ({target})")
    else:
        await msg.answer(f"Deleted url with alias ({target})")

def is_valid_url(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False