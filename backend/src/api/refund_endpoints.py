from fastapi import APIRouter

router = APIRouter()


@router.get("/cases")
async def get_refund_cases():
    return [{"id": "test-refund", "status": "Pending"}]


@router.post("/cases/{caseId}/refunds")
async def create_refund_request(caseId: str):
    return {"id": "new-refund", "status": "Pending"}
