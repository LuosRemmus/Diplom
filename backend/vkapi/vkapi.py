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
            "count": post_model.count
        }

        async with self.session() as session:
            async with session.get(url="https://api.vk.com/method/wall.get", params=params) as response:
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    posts = resp["response"]["items"]

                    out_post_models: list[OutPostModel] = []
                    for post in posts:
                        text = post["text"]
                        post.setdefault("signer_id", None)
                        
                        
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

                    logging.info(f"[GET POSTS] Количество постов: {len(out_post_models)}")
                    return out_post_models

    async def get_comments(self, comment_model: InCommentModel) -> list[OutCommentModel] | None:
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
                if response.status == status.HTTP_200_OK:
                    resp = await response.json()
                    if "response" not in resp:
                        return None
                    else:
                        comments = resp["response"]["items"]

                        out_comment_models: list[OutCommentModel] = []

                        for comment in comments:
                            text = comment["text"]
                            analyzer = Analyzer(text)
                            flag_type = analyzer.check_for_flag()
                            if flag_type:
                                author_id = comment["from_id"]
                                if author_id < 0:
                                    continue

                                thread = comment["thread"]["items"]
                                for th in thread:
                                    th_text = th["text"]

                                    th_analyzer = Analyzer(th_text)
                                    th_flag_type = th_analyzer.check_for_flag()

                                    if th_flag_type is not None:
                                        th_author_id = th["from_id"]
                                        if th_author_id < 0:
                                            continue

                                        current_th = OutCommentModel(
                                            author_id=th_author_id,
                                            text=th_text,
                                            flag_type=th_flag_type.value
                                        )
                                        out_comment_models.append(current_th)

                                current_comment = OutCommentModel(
                                    author_id=author_id,
                                    text=text,
                                    flag_type=flag_type.value
                                )
                                out_comment_models.append(current_comment)

                        return out_comment_models

    async def get_groups(self, group_model: InGroupModel) -> list[OutGroupModel]:
        if group_model.user_id > 0:
            params = {
                "access_token": self.access_token,
                "v": self.api_version,
                "user_id": group_model.user_id,
                "extended": group_model.extended
            }
            async with self.session() as session:
                async with session.get(url="https://api.vk.com/method/groups.get", params=params) as response:
                    if response.status == status.HTTP_200_OK:
                        resp = await response.json()
                        if "error" in resp:
                            return [OutGroupModel(
                                group_id=10101010,
                                group_name="Profile is private",
                                screen_name="Profile_is_private",
                            )]
                        groups = resp["response"]["items"]

                        out_group_models: list[OutGroupModel] = []
                        for group in groups:
                            current_model = OutGroupModel(
                                group_id=group["id"],
                                group_name=group["name"],
                                screen_name=group["screen_name"]
                            )

                            out_group_models.append(current_model)
                        return out_group_models
        return []
