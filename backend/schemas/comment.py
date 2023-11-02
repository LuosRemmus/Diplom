from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl


class InCommentModel(BaseModel):
    owner_id: int = Field(
        title="Group ID",
        lt=0,
        examples=[-1234567]
    )
    post_id: int = Field(
        title="Post ID",
        examples=[7654321]
    )
    count: int = Field(
        title="Comments count",
        ge=10,
        le=100,
        default=100,
        examples=[100]
    )
    offset: int | None = Field(
        title="Offset",
        ge=0,
        default=None,
        examples=[None, 1, 3, 10, 44, 79]
    )
    need_likes: int = Field(
        title="Reactions",
        ge=0,
        le=1,
        default=1,
        examples=[0, 1]
    )
    thread_items_count: int = Field(
        title="",
        ge=0,
        le=10,
        default=10,
        examples=[""]
    )


class OutCommentModel(BaseModel):
    author_id: int = Field(
        title="ID of comment author",
        gt=0,
        examples=[18534223]
    )
    text: str = Field(
        title="Comment text",
        examples=[
            "Обострение в зоне израильско-палестинского конфликта что известно к исходу 31 октября 2023 года"
        ]
    )
    flag_type: str = Field(
        title="Red or Yellow flag",
        examples=[
            "redflag",
            "yellowflag"
        ]
    )
    thread: list[OutCommentModel]
