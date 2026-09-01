import uuid
from repository.storage_repository import StorageRepository


class StorageService:
    def __init__(self, repository: StorageRepository):
        self.repository = repository

    async def request_upload_url(self, device_id: str, content_type: str) -> dict:
        extension = content_type.split("/")[-1]  # "image/jpeg" -> "jpeg"
        object_key = f"devices/{device_id}/{uuid.uuid4()}.{extension}"
        url = await self.repository.generate_presigned_put(object_key, content_type)
        return {"upload_url": url, "object_key": object_key}