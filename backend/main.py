from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from backend.vkapi import VKAdapter

from backend.schemas.post import InPostModel
from backend.schemas.user import InUserModel
from backend.schemas.comment import InCommentModel
from backend.schemas.group import InGroupModel

from backend.deploy.config import ACCESS_TOKEN, API_VERSION

app = FastAPI(title="VKApp")

app.mount(
    path="/frontend/media",
    app=StaticFiles(directory="frontend/media"),
    name="media")

templates = Jinja2Templates(directory="frontend/templates")


@app.get("/search")
def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/group_wall")
async def group_wall(domain: str, request: Request):
    vkadapter = VKAdapter(ACCESS_TOKEN, API_VERSION)
    all_groups = {}
    all_posts = []
    posts = await vkadapter.get_posts(InPostModel(domain=domain))

    for post in posts:
        comments = await vkadapter.get_comments(InCommentModel(owner_id=post.group_id, post_id=post.post_id))

        current_post_data = {
            "post_url": f"https://{domain}?w=wall{post.group_id}_{post.post_id}",
            "post_author": post.author_id,
            "flag_type": post.flag_type,
            "post_text": post.text,
            "comments": []
        }

        for comment in comments:
            author = await vkadapter.get_user(InUserModel(user_id=comment.author_id))

            current_post_data["comments"].append({
                "author_data": author.model_dump(),
                "text": comment.text,
                "flag_type": comment.flag_type,
                "thread": []
            })

            groups = await vkadapter.get_groups(InGroupModel(user_id=comment.author_id))
            for group in groups:
                all_groups.setdefault(group.group_url, [])
                all_groups[group.group_url].append(author.user_url)

            for th in comment.thread:
                th_user = (await vkadapter.get_user(InUserModel(user_id=th.author_id)))
                current_post_data["comment"]["thread"].append({
                    "author_data": th_user.model_dump(),
                    "text": th.text
                })

                th_groups = await vkadapter.get_groups(InGroupModel(user_id=th.author_id))

                for th_group in th_groups:
                    all_groups.setdefault(th_group.group_url, [])
                    all_groups[th_group.group_url].append(th_user.user_url)

            all_posts.append(current_post_data)

    return templates.TemplateResponse(
        name="group_wall.html",
        context={
            "request": request,
            "posts": all_posts,
            "groups": all_groups
        }
    )
