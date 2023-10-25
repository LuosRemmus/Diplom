from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from backend.vkapi import get_posts, get_comments, get_users, get_groups

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
def group_wall(domain: str, request: Request):
    result = []
    posts = get_posts(domain, count=1)["data"]

    for post in posts:
        post_data = {
            "post_url": f"vk.com/{domain}?w=wall{post['owner_id']}_{post['post_id']}",
            "post_text": post["text"],
            "comments": []
        }
        try:
            post_data["main_villain"] = f"vk.com/id{post['signer_id']}"
        except KeyError:
            post_data["main_villain"] = "Автор поста не указан"

        comments = get_comments(
            post["owner_id"],
            post["post_id"]
        )

        for comment in comments:
            comment_data = {
                "comment_text": comment["text"]
            }
            comment_author = get_users(str(comment))[0]
            comment_data["comment_author"]["author_data"] = comment_author

            comment_thread_users = get_users(",".join(str(thread_user["user_id"] for thread_user in comment["thread"])))
            comment_data["comment_author"]["comment_thread_users"] = comment_thread_users

            try:
                comment_data["comment_author"]["groups"] = get_groups(comment_author[0]["user_id"])
            except KeyError:
                print(f"Profile vk.com/id{comment['user_id']} is private")

            for thread_user in comment_data["comment_author"]["comment_thread_users"]:
                thread_user["groups"] = []
                try:
                    thread_user_groups = get_groups(thread_user["user_id"])
                    thread_user["groups"].append(thread_user_groups)
                except KeyError:
                    print(f"profile vk.com/id{thread_user['user_id']} is private")

            post_data["comments"].append(comment_data)

        result.append(post_data)
    return templates.TemplateResponse("group_wall.html", {"request": request, "data": result})
