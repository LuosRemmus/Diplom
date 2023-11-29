import logging

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend.routers.tgrouter import tgrouter, client
from backend.routers.vkrouter import vkrouter

logging.basicConfig(
    level=logging.INFO,
    filename="main.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)

templates = Jinja2Templates(directory="frontend/templates")

app = FastAPI(title="Application")

app.include_router(vkrouter)
app.include_router(tgrouter)


@app.get("/")
async def redirect_to_search():
    return RedirectResponse("/search")


@app.get("/search")
async def search(request: Request):
    await client.start()
    return templates.TemplateResponse("search.html", {"request": request})
