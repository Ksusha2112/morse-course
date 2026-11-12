from pydantic import BaseModel, Field


class EncodeRequest(BaseModel):
    text: str = Field(..., description="Исходный текст для кодирования")


class EncodeResponse(BaseModel):
    original: str
    morse: str


class DecodeRequest(BaseModel):
    morse: str


class DecodeResponse(BaseModel):
    morse: str
    text: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str