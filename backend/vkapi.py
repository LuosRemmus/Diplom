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

    async def get_posts(self, post_model: InPostModel) -> list[OutPostModel]:
        params = {
            'access_token': self.access_token,
            'v': self.api_version,
            'domain': post_model.domain,
            'count': post_model.count
        }
        if post_model.offset:
            params.update({'offset': post_model.offset})

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/wall.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    return resp["response"]["items"]

        # if response.status_code == status.HTTP_200_OK:
        #     posts = response.json()["response"]["items"]
        #     for post in posts:
        #         if is_unixtime_today(post['date']):
        #             if is_target_text(post["text"]):
        #                 post_data = {
        #                     "text": post["text"],
        #                     "owner_id": post["owner_id"],
        #                     "post_id": post["id"]
        #                 }
        #                 try:
        #                     post_data["signer_id"] = post["signer_id"]
        #                 except KeyError:
        #                     pass
        #                 result.append(post_data)

    async def get_comments(self, comment_model: InCommentModel) -> list[OutCommentModel]:
        params = {
            'access_token': self.access_token,
            'v': self.api_version,
            'owner_id': comment_model.owner_id,
            'post_id': comment_model.post_id,
            'count': comment_model.count,
            'need_likes': comment_model.need_likes,
            'thread_items_count': comment_model.thread_items_count
        }
        if comment_model.offset:
            params.update({'offset': comment_model.offset})

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/wall.getComments", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    return resp["response"]["items"]

        # if response.status_code == status.HTTP_200_OK:
        #     comments = response.json()["response"]["items"]
        #     for comment in comments:
        #         if is_target_text(comment["text"]):
        #             result.append({
        #                 "user_id": comment["from_id"],
        #                 "text": comment["text"],
        #                 "thread": [
        #                     {
        #                         "user_id": item["from_id"],
        #                         "text": item["text"],
        #                         "reply_to_user": item["reply_to_user"],
        #                         "reply_to_comment": item["reply_to_comment"]
        #                     }
        #                     for item in comment["thread"]["items"] if item["text"]]
        #             })
        #
        #     return result
        #
        # else:
        #     return {'status': response.status_code, 'message': 'error'}

    async def get_users(self, user_model: InUserModel) -> OutUserModel:
        params = {
            "access_token": self.access_token,
            'v': self.api_version,
            "user_ids": user_model.user_id,
            "fields": user_model.fields
        }

        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/users.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    return resp["response"]

        # if response.status_code == status.HTTP_200_OK:
        #     users = response.json()["response"]
        #     for user in users:
        #         temp_user_data = {"user_id": user["id"]}
        #
        #         try:
        #             temp_user_data["bdate"] = user["bdate"]
        #         except KeyError:
        #             temp_user_data["bdate"] = "Нет данных"
        #
        #         try:
        #             temp_user_data["country"] = user["country"]["title"]
        #         except KeyError:
        #             temp_user_data["country"] = "Нет данных"
        #
        #         try:
        #             temp_user_data["city"] = user["city"]["title"]
        #         except KeyError:
        #             temp_user_data["city"] = "Нет данных"
        #
        #         try:
        #             temp_user_data["photo_url"] = user["photo_max_orig"]
        #         except KeyError:
        #             temp_user_data["photo_url"] = "Нет данных"
        #
        #         try:
        #             temp_user_data["sex"] = "male" if user["sex"] == 2 else "female"
        #         except KeyError:
        #             temp_user_data["sex"] = "Нет данных"
        #
        #         result.append(temp_user_data)
        #
        #     return result
        #
        # else:
        #     return {"status": response.status_code, "message": "error"}

    async def get_groups(self, group_model: InGroupModel) -> OutGroupModel:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "user_id": group_model.user_id
        }
        async with self.session as session:
            async with session.get(url="https://api.vk.com/method/groups.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    return resp["response"]["items"]
