from typing import Annotated

from fastapi import Query
from requests import get
from starlette import status

from backend.analyzer import is_target_text, is_unixtime_today
from backend.config import ACCESS_TOKEN, API_VERSION

"""
Советую выделить эти методы в отдельный класс и реализовать с помощью aiohttp
таким образом получится чуть правильнее организовать всю работу

Примерно такой API должен быть

class VKAdapter:
    async def get_posts(...) -> dict:
        pass
    async def get_comments(...) -> list[dict] | dict[str, str | int]:
        pass
    async def get_users(...) -> list[dict] | dict[str, str | int]:
        pass
    async def get_groups(...) -> list[str] | dict[str, str | int]:

При этом настоятельно рекомендую сделать инициализацию сессии прям в конструкторе, чтобы выглядело примерно так:

    def __init__(self, access_token: str, api_version: str) -> None:
        self.session = ClientSession()

Внутри методов, по хорошему, можно сделать DTO и превратить файл vkapi.py в полноценный адаптер

Возвращать ошибки в виде словарей, на самом деле вообще не советую. Либо кастомные ошибки, либо тогда хотя бы DTO

================================================================
   try:
        temp_user_data["bdate"] = user["bdate"]
    except KeyError:
        temp_user_data["bdate"] = "Нет данных"

    try:
        temp_user_data["country"] = user["country"]["title"]
    except KeyError:
        temp_user_data["country"] = "Нет данных"
================================================================

Вот такого рода вещи советую всё таки гонять хотя бы через pydantic модели. И в целом, к предыдущему пункту это своего рода плюсик
"""


def get_posts(
    domain: str,
    count: Annotated[int | None, Query(ge=10, le=100)] = 100,
    offset: int | None = None,
) -> dict:
    result = []
    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "domain": domain,
        "count": count,
    }
    if offset:
        params.update({"offset": offset})

    response = get(url="https://api.vk.com/method/wall.get", params=params)

    if response.status_code == status.HTTP_200_OK:
        posts = response.json()["response"]["items"]
        for post in posts:
            if is_unixtime_today(post["date"]):
                if is_target_text(post["text"]):
                    post_data = {
                        "text": post["text"],
                        "owner_id": post["owner_id"],
                        "post_id": post["id"],
                    }
                    try:
                        post_data["signer_id"] = post["signer_id"]
                    except KeyError:
                        pass
                    result.append(post_data)
        return {"status": status.HTTP_200_OK, "data": result}
    else:
        return {"status": response.status_code, "message": "error"}


def get_comments(
    owner_id: int,
    post_id: int,
    count: Annotated[int, Query(ge=10, le=100)] = 100,
    offset: int | None = None,
    need_likes: int = 1,
    thread_items_count: int = 10,
) -> list[dict] | dict[str, str | int]:
    result = []
    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "owner_id": owner_id,
        "post_id": post_id,
        "count": count,
        "need_likes": need_likes,
        "thread_items_count": thread_items_count,
    }
    if offset:
        params.update({"offset": offset})

    response = get(url="https://api.vk.com/method/wall.getComments", params=params)

    if response.status_code == status.HTTP_200_OK:
        comments = response.json()["response"]["items"]
        for comment in comments:
            if is_target_text(comment["text"]):
                result.append(
                    {
                        "user_id": comment["from_id"],
                        "text": comment["text"],
                        "thread": [
                            {
                                "user_id": item["from_id"],
                                "text": item["text"],
                                "reply_to_user": item["reply_to_user"],
                                "reply_to_comment": item["reply_to_comment"],
                            }
                            for item in comment["thread"]["items"]
                            if item["text"]
                        ],
                    }
                )

        return result

    else:
        return {"status": response.status_code, "message": "error"}


def get_users(user_ids: str) -> list[dict] | dict[str, str | int]:
    result = []
    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "user_ids": user_ids,
        "fields": "bdate, city, country, photo_max_orig, sex, verified",
    }

    response = get(url="https://api.vk.com/method/users.get", params=params)

    if response.status_code == status.HTTP_200_OK:
        users = response.json()["response"]
        for user in users:
            temp_user_data = {"user_id": user["id"]}

            try:
                temp_user_data["bdate"] = user["bdate"]
            except KeyError:
                temp_user_data["bdate"] = "Нет данных"

            try:
                temp_user_data["country"] = user["country"]["title"]
            except KeyError:
                temp_user_data["country"] = "Нет данных"

            try:
                temp_user_data["city"] = user["city"]["title"]
            except KeyError:
                temp_user_data["city"] = "Нет данных"

            try:
                temp_user_data["photo_url"] = user["photo_max_orig"]
            except KeyError:
                temp_user_data["photo_url"] = "Нет данных"

            try:
                temp_user_data["sex"] = "male" if user["sex"] == 2 else "female"
            except KeyError:
                temp_user_data["sex"] = "Нет данных"

            result.append(temp_user_data)

        return result

    else:
        return {"status": response.status_code, "message": "error"}


def get_groups(user_id: int) -> list[str] | dict[str, str | int]:
    params = {"access_token": ACCESS_TOKEN, "v": API_VERSION, "user_id": user_id}
    response = get(url="https://api.vk.com/method/groups.get", params=params)
    if response.status_code == status.HTTP_200_OK:
        return response.json()["response"]["items"]
    else:
        return {"status": response.status_code, "message": "error"}
