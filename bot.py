from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
import os

from repository.repository import RepositorySystem
from config.config import ConfigSystem
from provider.provider import ProviderSystem

from typing import List

CONFIG: ConfigSystem = None
REPOSITORY: RepositorySystem = None
PROVIDER: ProviderSystem = None

MSG: List[Message] = list()

dp = Dispatcher()

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Bot started")
    global MSG
    MSG.append(msg)

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

    if not ProviderSystem.REGISTRY[provider]:
        await msg.answer("Incorrect provider")
        return

    await REPOSITORY.add_site(url, alias)
    await msg.answer(f"Added: {url} (alias: {alias}, provider: {provider})")

@dp.message(Command("remove"))
async def remove(msg: Message):
    args = msg.text.split()[1:]
    
    if not args:
        await msg.answer("Incorrect alias")
        return
    
    target = args[0]

    if await is_valid_url(target):
        await REPOSITORY.delete_site(target)
        await msg.answer(f"Removed url ({target})")
    else:
        await REPOSITORY.delete_site(await REPOSITORY.get_url(target))
        await msg.answer(f"Removed url with alias ({target})")

@dp.message(Command("list"))
async def list(msg: Message):
    sites = await REPOSITORY.get_all_sites()
    sites_text = "\n * ".join([f"{alias}: {url}" for url, alias in sites])
    await msg.answer(f"Sites:\n{sites_text}")

@dp.message(Command("time"))
async def time(msg: Message):
    args = msg.text.split()[1:]
    
    if not args:
        await msg.answer("Incorrect timezone")
        return

    CONFIG.set("DAYDIGEST", args[0])
    
@dp.message(Command("set_timezone"))
async def set_timezone(msg: Message):
    args = msg.text.split()[1:]
    
    if not args:
        await msg.answer("Incorrect timezone")
        return

    CONFIG.set("TZ", args[0])

    await msg.answer("Timezone updated")

async def notificate():
    for site in REPOSITORY.get_all_site():
        pass

    global MSG
    for msg in MSG:
        msg.answer()


async def is_valid_url(url: str) -> bool:
    import re
    
    regex = re.compile(
        r'^(https?|ftp)://'
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
        r'(:[0-9]{1,5})?'
        r'(/.*)?$'
    )
    return bool(regex.match(url))
    
async def start(config: ConfigSystem, repository: RepositorySystem, provider: ProviderSystem):
    global CONFIG, REPOSITORY, PROVIDER

    bot = Bot(token=os.getenv("TOKEN"))

    CONFIG = config
    REPOSITORY = repository
    PROVIDER = provider

    await dp.start_polling(bot)