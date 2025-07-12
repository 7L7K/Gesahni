from fastapi import APIRouter

router = APIRouter(prefix="/enroll")

@router.get("/")
async def read_root():
    return {"message": "enroll root"}
