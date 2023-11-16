import logging

from starlette import status
from aiohttp import ClientSession

from backend.analyzer.analyzer import Analyzer

from backend.schemas.post import InPostModel, OutPostModel
from backend.schemas.comment import InCommentModel, OutCommentModel
from backend.schemas.group import InGroupModel, OutGroupModel

logging.basicConfig(
    level=logging.INFO,
    filename="VKAdapter.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)


class VKAdapter:
    def __init__(self, access_token: str, api_version: str):
        self.access_token = access_token
        self.api_version = api_version
        self.session = ClientSession

    async def get_posts(self, post_model: InPostModel) -> list[OutPostModel | None]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "domain": post_model.domain,
            "count": 2  # post_model.count
        }

        async with self.session() as session:
            async with session.get(url="https://api.vk.com/method/wall.get", params=params) as response:
                logging.info("[GET POSTS] Получен ответ от api.vk.com")
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    posts = resp["response"]["items"]

                    out_post_models: list[OutPostModel] = []
                    for post in posts:
                        post.setdefault("signer_id", None)

                        text = post["text"]
                        date = post["date"]

                        analyzer = Analyzer(text)

                        # if analyzer.is_unixtime_today(date):
                        post_id = post["id"]
                        group_id = post["owner_id"]
                        author_id = post["signer_id"]

                        current_model = OutPostModel(
                            post_id=post_id,
                            group_id=group_id,
                            author_id=author_id,
                            text=text
                        )

                        out_post_models.append(current_model)
                        # else:
                        #     break
                    logging.info(f"[GET POSTS] Количество постов: {len(out_post_models)}")
                    logging.info("[GET POSTS] Конец работы функции")
                    return out_post_models

    async def get_comments(self, comment_model: InCommentModel) -> list[OutCommentModel]:
        logging.info(f"[GET COMMENTS] Модель комментария на вход: {comment_model}")
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

        async with self.session() as session:
            async with session.get(url="https://api.vk.com/method/wall.getComments", params=params) as response:
                logging.info("[GET COMMENTS] Получен ответ от api.vk.com")

                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    comments = resp["response"]["items"]

                    out_comment_models: list[OutCommentModel] = []

                    for comment in comments:
                        text = comment["text"]
                        analyzer = Analyzer(text)
                        flag_type = analyzer.check_for_flag()
                        # if analyzer.is_unixtime_today(comment["date"]):
                        #     if flag_type:
                        author_id = comment["from_id"]
                        text = comment["text"]

                        thread = comment["thread"]["items"]
                        out_thread_models: list[OutCommentModel] = []
                        for th in thread:
                            th_author_id = th["from_id"]
                            th_text = th["text"]

                            current_th = OutCommentModel(
                                author_id=th_author_id,
                                text=th_text
                            )

                            out_thread_models.append(current_th)

                        current_comment = OutCommentModel(
                            author_id=author_id,
                            text=text,
                            thread=out_thread_models
                        )
                        logging.info(f"[GET COMMENTS] Данные комментария: {current_comment.dict()}")
                        out_comment_models.append(current_comment)
                        # else:
                        #     break
                    return out_comment_models

    async def get_groups(self, group_model: InGroupModel) -> list[OutGroupModel]:
        params = {
            "access_token": self.access_token,
            "v": self.api_version,
            "user_id": group_model.user_id,
            "extended": group_model.extended
        }
        async with self.session() as session:
            async with session.get(url="https://api.vk.com/method/groups.get", params=params) as response:
                logging.info("[GET GROUPS] получен ответ от api.vk.com")
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    if "error" in resp:
                        return [OutGroupModel(
                            group_id=10101010,
                            group_name="Profile is private",
                            group_url="https://Profile_is_private.com",
                        )]
                    groups = resp["response"]["items"]

                    out_group_models: list[OutGroupModel] = []
                    for group in groups:
                        group_id = group["id"]
                        group_name = group["name"]
                        group_url = "https://vk.com/" + group["screen_name"]

                        current_model = OutGroupModel(
                            group_id=group_id,
                            group_name=group_name,
                            group_url=group_url
                        )

                        logging.info(f"[GET GROUPS] Данные групп: {current_model.dict()}")

                        out_group_models.append(current_model)
                    return out_group_models
