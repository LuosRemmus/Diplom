from pydantic import BaseModel, Field, HttpUrl


class InUserModel(BaseModel):
    user_id: int = Field(
        title="User ID",
        gt=0,
        examples=[12345678, 87654321]
    )
    fields: str = Field(
        title="Fields, which need to get",
        default="bdate, city, country, photo_max_orig, sex, verified",
        examples=["bdate, city, country, photo_max_orig, sex, verified"]
    )


class OutUserModel(BaseModel):
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
        examples=[
            "https://sun1-13.userapi.com/s/v1/ig2/KIR0-JA9L-TeAsSxmVNnUBH8cALig9l9RJd1VReYfWCu8IJaEgyr06LYAmttBizR8tp_foH9k3y4f4PT64E1s6Dw.jpg?size=400x400&quality=95&crop=0,276,1920,1920&ava=1"
        ]
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
