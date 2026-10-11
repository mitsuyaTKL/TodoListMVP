from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok"}

@router.get("/", tags=["system"])
def root() -> dict:
    return {
        "service": "Todo List by Mitsuya",
        "docs": "/docs",
        "health": "/health",
    }