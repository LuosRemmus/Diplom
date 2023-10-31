from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class Flag(Enum):
    redflag = "redflag"
    yellowflag = "yellowflag"


class Post(BaseModel):
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
        examples=["Обострение в зоне израильско-палестинского конфликта что известно к исходу 31 октября 2023 года"]
    )


class Comment(BaseModel):
    author_id: int = Field(
        title="ID of comment author",
        gt=0,
        examples=[18534223]
    )
    text: str = Field(
        title="Comment text",
        examples=["Обострение в зоне израильско-палестинского конфликта что известно к исходу 31 октября 2023 года"]
    )
    flag_type: str = Field(
        title="Red or Yellow flag",
        examples=[
            "redflag",
            "yellowflag"
        ]
    )
    thread: list[Comment]


class User(BaseModel):
    fname: str = Field(
        title="User's first name",
        examples=["Петр", "Иван", "Сидор"]
    )
    lname: str = Field(
        title="User's last name",
        examples=["Петров", "Иванов", "Сидоров"]
    )
    photo: HttpUrl = Field(
        title="URL of user's photo",
        examples=["https://sun1-13.userapi.com/s/v1/ig2/KIR0-JA9L-TeAsSxmVNnUBH8cALig9l9RJd1VReYfWCu8IJaEgyr06LYAmttBizR8tp_foH9k3y4f4PT64E1s6Dw.jpg?size=400x400&quality=95&crop=0,276,1920,1920&ava=1"]
    )
    user_url: HttpUrl = Field(
        title="User URL",
        examples=["https://vk.com/id12345678"]
    )
    city: str | None = Field(
        title="User's city",
        default=None,
        examples=["Москва", "Санкт-Петербург", "Курск", "Липецк", "Воронеж"]
    )
    country: str | None = Field(
        title="User's country",
        default=None,
        examples=["Россия", "Белоруссия", "Казахстан"]
    )
    bdate: str | None = Field(
        title="User's birth date",
        default=None,
        examples=["12.12.2000", "12.12"]
    )
    sex: str | None = Field(
        title="User's sex",
        default=None,
        examples=["male", "female"]
    )


class Group(BaseModel):
    group_id: int = Field(
        title="ID of group",
        examples=[30684458]
    )
    group_url: HttpUrl = Field(
        title="Group URL",
        examples=["https://vk.com/rybar_force"]
    )
