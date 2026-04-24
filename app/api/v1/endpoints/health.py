from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/",
    summary="Health check",
    description="Check if API is running",
)
def health():
    return {"status": "ok"}