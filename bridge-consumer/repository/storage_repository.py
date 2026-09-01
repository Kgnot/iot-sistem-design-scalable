import boto3
import asyncio
from config.r2_config import R2Config


class StorageRepository:
    def __init__(self, config: R2Config):
        self.config = config
        self._client = boto3.client(
            "s3",
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            region_name="auto",
        )

    async def generate_presigned_put(self, object_key: str, content_type: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.config.bucket,
                    "Key": object_key,
                    "ContentType": content_type,
                },
                ExpiresIn=self.config.presign_expires_seconds,
            ),
        )