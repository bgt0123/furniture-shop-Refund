from fastapi import APIRouter

router = APIRouter()


@router.get("/refunds/cases")
async def get_all_refund_cases():
    return [{"id": "test-admin-refund", "status": "Pending"}]


@router.post("/refunds/cases/{refundId}/approve")
async def approve_refund(refundId: str):
    return {"id": refundId, "status": "Approved"}
