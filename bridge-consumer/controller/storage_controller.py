from fastapi import APIRouter, Depends
from pydantic import BaseModel

from service.storage_service import StorageService
from config.dependencies import get_storage_service

router = APIRouter(prefix="/storage", tags=["storage"])


class PresignRequest(BaseModel):
    device_id: str
    content_type: str


@router.post("/presign-upload")
async def presign_upload(
    body: PresignRequest,
    storage_service: StorageService = Depends(get_storage_service),
):
    return await storage_service.request_upload_url(body.device_id, body.content_type)