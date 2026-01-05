from fastapi import APIRouter

router = APIRouter()


@router.get("/cases")
async def get_support_cases():
    return [{"id": "test", "status": "Open"}]


@router.post("/cases")
async def create_support_case():
    return {"id": "new-case", "status": "Open"}
