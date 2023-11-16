import asyncio
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


@app.get("/")
def redirect_to_search():
    return RedirectResponse("/search")


@app.get("/search")
def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/group_wall")
async def group_wall(domain: str, request: Request):
    vkadapter = VKAdapter(ACCESS_TOKEN, API_VERSION)

    all_groups = {}
    all_posts = []

    async def producer(tasks: list, queue: asyncio.Queue):
        for task in tasks:
            await queue.put(task)

    async def post_consumer(queue: asyncio.Queue):
        while True:
            task = await queue.get()
            users = []
            post_data = {
                "post_url": f"https://{domain}?w=wall{task.group_id}_{task.post_id}",
                "post_text": task.text,
                "comments": []
            }
            post_comments = await vkadapter.get_comments(
                InCommentModel(owner_id=task.group_id, post_id=task.post_id)
            )

            for post_comment in post_comments:
                comment_data = {
                    "author_id": post_comment.author_id,
                    "text": post_comment.text,
                    "flag_type": post_comment.flag_type
                }

                users.append(InGroupModel(user_id=post_comment.author_id))

                post_data["comments"].append(comment_data)

                for th in post_comment.thread:
                    comment_data = {
                        "author_id": th.author_id,
                        "text": th.text,
                        "flag_type": th.flag_type
                    }

                    users.append(InGroupModel(user_id=th.author_id))

                    post_data["comments"].append(comment_data)

            all_posts.append(post_data)

            user_queue = asyncio.Queue(maxsize=100)

            for _ in range(10):
                asyncio.create_task(user_consumer(user_queue))

            await producer(users, user_queue)
            await user_queue.join()

            queue.task_done()

    async def user_consumer(queue: asyncio.Queue):
        while True:
            task = await queue.get()
            user_groups = await vkadapter.get_groups(task)
            for user_group in user_groups:
                if user_group.group_url not in all_groups:
                    all_groups.setdefault(user_group.group_url, [])
                if task not in all_groups[user_group.group_url]:
                    all_groups[user_group.group_url].append(task)

            queue.task_done()

    posts = await vkadapter.get_posts(InPostModel(domain=domain))

    post_queue = asyncio.Queue(maxsize=100)
    for _ in range(10):
        asyncio.create_task(post_consumer(post_queue))

    await producer(posts, post_queue)
    await post_queue.join()

    return templates.TemplateResponse(
        "group_wall.html",
        {
            "request": request,
            "posts": all_posts,
            "groups": all_groups
        }
    )
