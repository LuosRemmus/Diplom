from pydantic import BaseModel, Field, HttpUrl


class InGroupModel(BaseModel):
    user_id: int = Field(
        title="User ID",
        gt=0,
        examples=[12345678, 87654321]
    )
    extended: int = Field(
        title="Group info",
        ge=0,
        le=1,
        default=1,
        examples=[0, 1]
    )


class OutGroupModel(BaseModel):
    group_id: int = Field(
        title="ID of group",
        examples=[30684458]
    )
    group_name: str = Field(
        title="Group name",
        examples=["BEST of MMA", "Рыбарь"]
    )
    group_url: HttpUrl = Field(
        title="Group URL",
        examples=["https://vk.com/rybar_force"]
    )
