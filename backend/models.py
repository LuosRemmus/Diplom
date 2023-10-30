from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class Flag(Enum):
    redflag = "redflag"
    yellowflag = "yellowflag"


class Post(BaseModel):
    post_id: int = Field(title="ID of VK post", gt=0)
    group_id: int = Field(title="ID of VK group", lt=0)
    author_id: int | None = Field(title="ID of post author", gt=0, default=None)
    flag_type: Flag = Field(title="Red or Yellow flag")
    text: str = Field(title="Post text")


class Comment(BaseModel):
    author_id: int = Field(title="ID of comment author", gt=0)
    text: str = Field(title="Comment text")
    flag_type: str = Field(title="Red or Yellow flag")
    thread: list[Comment]


class User(BaseModel):
    fname: str = Field(title="User's first name")
    lname: str = Field(title="User's last name")
    photo: HttpUrl = Field(title="URL of user's photo")
    user_url: HttpUrl = Field(title="User URL")
    city: str | None = Field(title="User's city", default=None)
    country: str | None = Field(title="User's country", default=None)
    bdate: str | None = Field(title="User's birth date", default=None)
    sex: str | None = Field(title="User's sex", default=None)


class Group(BaseModel):
    group_id: int = Field(title="ID of group")
    group_url: HttpUrl = Field(title="Group URL")
