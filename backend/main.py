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

    return templates.TemplateResponse("group_wall.html", {"request": request, "data": result})
