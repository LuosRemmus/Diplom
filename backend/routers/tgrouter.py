import asyncio
import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from backend.deploy.config import API_HASH, API_ID
from telethon import TelegramClient

templates = Jinja2Templates(directory="frontend/templates")
tgrouter = APIRouter(
    prefix="/tg",
    tags=["Telegram"]
)

comments = []
client = TelegramClient(session="session_name",
                        api_id=API_ID,
                        api_hash=API_HASH,
                        system_version="4.16.30-vxCUSTOM")


async def get_comments(channel_name: str, limit: int = 5000):
    messages = await client.get_messages(channel_name, limit=limit)
    for message in messages:
        try:
            comments.append(
                {
                    "channel": channel_name,
                    "user_id": message.from_id.user_id,
                    "message": message.message
                }
            )
        except AttributeError:
            pass
    return comments


async def consumer(queue: asyncio.Queue):
    while True:
        try:
            task = await queue.get()
            print(f"принял название канала: {task}")
            await get_comments(channel_name=task)
            queue.task_done()
        except Exception as ex:
            print(f"Ошибка, {ex}")
            logging.info(f"Error {ex}")


@tgrouter.get("/comments")
async def show_telegram_comments(request: Request, channels_names: str):
    print("Функция show_telegram_comments начала работу")
    channels_names = channels_names.split()
    print("Каналы:", channels_names)
    queue = asyncio.Queue(maxsize=100)
    for _ in channels_names:
        asyncio.create_task(consumer(queue))

    for ch_name in channels_names:
        await queue.put(ch_name)

    await queue.join()
    print("Функция закончила работу")
    print(f"Комментарии: {comments}")
    return templates.TemplateResponse(
        "tg-comments.html",
        {
            "request": request,
            "comments": comments
        }
    )


@tgrouter.get("/channels")
async def show_telegram_channels(request: Request):
    users = {}
    for item in comments:
        channel = item["channel"]
        user_id = item["user_id"]
        if users.get(user_id):
            if channel not in users[user_id]:
                users[user_id].append(channel)
        else:
            users[user_id] = [channel]

    users = {k: v for k, v in users.items() if len(v) >= 2}

    return templates.TemplateResponse(
        "tg-channels.html",
        {
            "request": request,
            "users": users
        }
    )
