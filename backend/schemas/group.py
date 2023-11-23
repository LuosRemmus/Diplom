from pydantic import BaseModel, Field


class InGroupModel(BaseModel):
    user_id: int = Field(
        title="User ID",
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
    screen_name: str = Field(
        title="Group domain",
        examples=["rybar_force"]
    )
