import asyncio
import json
import logging

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend.vkapi.vkapi import VKAdapter

from backend.schemas.post import InPostModel
from backend.schemas.comment import InCommentModel
from backend.schemas.group import InGroupModel

from backend.deploy.config import ACCESS_TOKEN, API_VERSION

logging.basicConfig(
    level=logging.INFO,
    filename="main.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)

app = FastAPI(title="VKApp")
templates = Jinja2Templates(directory="frontend/templates")
vkadapter = VKAdapter(ACCESS_TOKEN, API_VERSION)
all_groups = {}
all_posts = []
all_users = []


async def user_consumer(queue: asyncio.Queue):
    while True:
        task = await queue.get()
        user_groups = await vkadapter.get_groups(task)
        for user_group in user_groups:
            if user_group.screen_name not in all_groups:
                all_groups.setdefault(
                    user_group.screen_name,
                    {
                        "group_name": user_group.group_name,
                        "users": []
                    }
                )

            if f"https://vk.com/id{task.user_id}" not in all_groups[user_group.screen_name]["users"]:
                all_groups[user_group.screen_name]["users"].append(f"https://vk.com/id{task.user_id}")

        queue.task_done()


async def post_consumer(queue: asyncio.Queue, domain: str):
    while True:
        task = await queue.get()

        user_queue = asyncio.Queue(maxsize=100)
        for _ in range(10):
            asyncio.create_task(user_consumer(user_queue))

        post_data = {
            "post_url": f"https://vk.com/{domain}?w=wall{task.group_id}_{task.post_id}",
            "post_text": task.text,
            "comments": []
        }
        post_comments = await vkadapter.get_comments(
            InCommentModel(
                owner_id=task.group_id,
                post_id=task.post_id
            )
        )
        if post_comments is not None:
            for post_comment in post_comments:
                comment_data = {
                    "author_id": post_comment.author_id,
                    "text": post_comment.text,
                    "flag_type": post_comment.flag_type
                }
                if post_comment.author_id not in all_users:
                    all_users.append(post_comment.author_id)
                    await user_queue.put(InGroupModel(user_id=post_comment.author_id))
                    post_data["comments"].append(comment_data)

            await user_queue.join()

        all_posts.append(post_data)

        queue.task_done()


@app.get("/")
def redirect_to_search():
    return RedirectResponse("/search")


@app.get("/search")
def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/vkposts")
async def show_vkposts(domain: str, request: Request):
    posts = await vkadapter.get_posts(InPostModel(domain=domain))

    post_queue = asyncio.Queue(maxsize=100)
    for _ in range(10):
        asyncio.create_task(post_consumer(post_queue, domain))

    for post in posts:
        await post_queue.put(post)

    await post_queue.join()

    with open("data_files/groups.json", "w", encoding="utf-8", errors='ignore') as file:
        groups_result = {key: value for key, value in all_groups.items() if len(value["users"]) >= 2}
        json.dump(groups_result, file, indent=2)

    return templates.TemplateResponse(
        "vk-posts.html",
        {
            "request": request,
            "posts": all_posts
        }
    )


@app.get("/vk-groups")
def show_vkgroups(request: Request):
    with open("data_files/groups.json", "r", encoding="utf-8", errors="ignore") as file:
        groups = json.load(file)

    for group in groups:
        groups[group]["num"] = list(groups.keys()).index(group) + 1

    return templates.TemplateResponse(
        "vk-groups.html",
        {
            "request": request,
            "groups": groups
        }
    )


@app.get("/telegram-comments")
def show_telegram_comments(request: Request):
    comments = ...
    return templates.TemplateResponse(
        "telegram-comments.html",
        {
            "request": request,
            "comments": comments
        }
    )


@app.get("/telegram-groups")
def show_telegram_groups(request: Request):
    groups = ...
    return templates.TemplateResponse(
        "telegram-groups.html",
        {
            "request": request,
            "groups": groups
        }
    )