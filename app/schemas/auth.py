import re

from pydantic import BaseModel, Field, field_validator


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserCreate(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Correo invalido")
        return value


class UserLogin(BaseModel):
    email: str = Field(max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Correo invalido")
        return value


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
