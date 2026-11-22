from fastapi import APIRouter
#import asyncio

router = APIRouter()

@router.get("/health", tags=["system"])
async def health_check() -> dict:
    #await asyncio.sleep(5)
    return {"status": "ok"}
