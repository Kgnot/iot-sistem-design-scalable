import os
from dataclasses import dataclass


@dataclass
class R2Config:
    account_id: str = os.getenv("R2_ACCOUNT_ID", "")
    access_key_id: str = os.getenv("R2_ACCESS_KEY_ID", "")
    secret_access_key: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    bucket: str = os.getenv("R2_BUCKET", "")
    presign_expires_seconds: int = 300
    endpoint_url_override: str = os.getenv("R2_ENDPOINT_URL_OVERRIDE", "")

    @property
    def endpoint_url(self) -> str:
        if self.endpoint_url_override:
            return self.endpoint_url_override
        return f"https://{self.account_id}.r2.cloudflarestorage.com"
