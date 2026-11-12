import os

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .morse import encode, decode
from .schemas import (
    EncodeRequest, EncodeResponse,
    DecodeRequest, DecodeResponse,
    HealthResponse,
)

STATS_SERVICE_URL = os.getenv("STATS_SERVICE_URL", "http://stats-service:8003")

app = FastAPI(title="Morse Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def update_stats(direction: str) -> None:
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{STATS_SERVICE_URL}/api/increment",
                json={"direction": direction},
                timeout=2.0,
            )
    except Exception as e:
        print(f"Stats error: {e}")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="morse", version=app.version)


@app.post("/api/encode", response_model=EncodeResponse)
async def api_encode(payload: EncodeRequest) -> EncodeResponse:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Пустой текст")
    morse = encode(payload.text)
    await update_stats("encode")
    return EncodeResponse(original=payload.text, morse=morse)


@app.post("/api/decode", response_model=DecodeResponse)
async def api_decode(payload: DecodeRequest) -> DecodeResponse:
    if not payload.morse.strip():
        raise HTTPException(status_code=400, detail="Пустая последовательность Морзе")
    text = decode(payload.morse)
    await update_stats("decode")
    return DecodeResponse(morse=payload.morse, text=text)


@app.post("/api/encode-file", response_model=EncodeResponse)
async def api_encode_file(file: UploadFile = File(...)) -> EncodeResponse:
    raw = await file.read()
    if len(raw) > 1_000_000:
        raise HTTPException(status_code=413, detail="Файл слишком большой")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1251")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Файл пуст")
    morse = encode(text)
    await update_stats("encode")
    return EncodeResponse(original=text, morse=morse)
