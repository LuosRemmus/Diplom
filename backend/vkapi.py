from starlette import status
from aiohttp import ClientSession

from backend.analyzer import Analyzer

from backend.schemas.post import InPostModel, OutPostModel
from backend.schemas.user import InUserModel, OutUserModel
from backend.schemas.comment import InCommentModel, OutCommentModel
from backend.schemas.group import InGroupModel, OutGroupModel


class VKAdapter:
    def __init__(self, access_token: str, api_version: str):
        self.access_token = access_token
        self.api_version = api_version
        self.session = ClientSession()

    async def get_posts(self, post_model: InPostModel) -> list[OutPostModel | None]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "domain": post_model.domain,
            "count": post_model.count
        }
        if post_model.offset:
            params.update({"offset": post_model.offset})

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/wall.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    posts = resp["response"]["items"]

        out_post_models: list[OutPostModel] = []
        for post in posts:
            post.setdefault("signer_id", None)

            text = post["text"]
            date = post["date"]

            analyzer = Analyzer(text)
            flag_type = analyzer.check_for_flag()

            if analyzer.is_unixtime_today(date):
                if flag_type:
                    post_id = post["id"]
                    group_id = post["owner_id"]
                    author_id = post["signer_id"]

                    out_post_models.append(OutPostModel(
                        post_id=post_id,
                        group_id=group_id,
                        author_id=author_id,
                        flag_type=flag_type,
                        text=text
                    ))
                else:
                    break
            else:
                continue

        return out_post_models

    async def get_comments(self, comment_model: InCommentModel) -> list[OutCommentModel]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "owner_id": comment_model.owner_id,
            "post_id": comment_model.post_id,
            "count": comment_model.count,
            "need_likes": comment_model.need_likes,
            "thread_items_count": comment_model.thread_items_count
        }
        if comment_model.offset:
            params.update({"offset": comment_model.offset})

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/wall.getComments", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    comments = resp["response"]["items"]

        out_comment_models: list[OutCommentModel] = []

        for comment in comments:
            text = comment["text"]
            analyzer = Analyzer(text)
            flag_type = analyzer.check_for_flag()
            if analyzer.is_unixtime_today(comment["date"]):
                if flag_type:
                    author_id = comment["from_id"]
                    text = comment["text"]

                    thread = comment["thread"]
                    out_thread_models: list[OutCommentModel] = []
                    for th in thread:
                        th_author_id = th["from_id"]
                        th_text = th["text"]
                        out_thread_models.append(OutCommentModel(
                            author_id=th_author_id,
                            text=th_text
                        ))
                    out_comment_models.append(OutCommentModel(
                        author_id=author_id,
                        text=text,
                        thread=out_thread_models
                    ))
            else:
                break
        return out_comment_models

    async def get_users(self, user_model: InUserModel) -> list[OutUserModel]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "user_ids": user_model.user_id,
            "fields": user_model.fields
        }

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/users.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    users = resp["response"]

        out_user_models: list[OutUserModel] = []
        for user in users:
            user.setdefault("photo_max_orig", None)
            user.setdefault("city", {"title": None})
            user.setdefault("country", {"title": None})
            user.setdefault("bdate", None)
            user.setdefault("sex", None)

            fname = user["first_name"]
            lname = user["last_name"]
            photo = user["photo_max_orig"]
            user_url = f"https://vk.com/id{user_model.user_id}"
            city = user["city"]["title"]
            country = user["country"]["title"]
            bdate = user["bdate"]
            match user["sex"]:
                case 1:
                    sex = "female"
                case 2:
                    sex = "male"
                case _:
                    sex = None

            out_user_models.append(OutUserModel(
                fname=fname,
                lname=lname,
                photo=photo,
                user_url=user_url,
                city=city,
                country=country,
                bdate=bdate,
                sex=sex
            ))
        return out_user_models

    async def get_groups(self, group_model: InGroupModel) -> list[OutGroupModel]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "user_id": group_model.user_id,
            "extended": 1
        }
        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/groups.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    groups = resp["response"]["items"]

        out_group_models: list[OutGroupModel] = []
        for group in groups:
            group_id = group["id"]
            group_name = group["name"]
            group_url = "https://vk.com/" + group["screen_name"]

            out_group_models.append(OutGroupModel(
                group_id=group_id,
                group_name=group_name,
                group_url=group_url
            ))
        return out_group_models
