from __future__ import annotations
from pydantic import BaseModel, Field

from backend.schemas.flag import Flag


class InPostModel(BaseModel):
    domain: str = Field(
        title="Group domain",
        examples=["best_of_mma", "rybar_force"]
    )
    count: int = Field(
        title="Posts count",
        ge=10,
        le=100,
        default=100
    )


class OutPostModel(BaseModel):
    post_id: int = Field(
        title="ID of VK post",
        gt=0,
        examples=[-30684458]
    )
    group_id: int = Field(
        title="ID of VK group",
        lt=0,
        examples=[18534223]
    )
    author_id: int | None = Field(
        title="ID of post author",
        gt=0,
        default=None,
        examples=[18534223]
    )
    flag_type: Flag = Field(
        title="Red or Yellow flag",
        examples=[
            "redflag",
            "yellowflag"
        ]
    )
    text: str = Field(
        title="Post text",
        examples=[
            "Обострение в зоне израильско-палестинского конфликта что известно к исходу 31 октября 2023 года"
        ]
    )
