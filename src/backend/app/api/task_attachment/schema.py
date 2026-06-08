import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

class TaskAttachmentBase(BaseModel):
    file_name: str
    file_url: str
    type: str

class TaskAttachmentCreate(TaskAttachmentBase):
    task_id: uuid.UUID

class TaskAttachmentResponse(TaskAttachmentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AddLinkRequest(BaseModel):
    title: Optional[str] = None
    url: HttpUrl

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Judul lampiran tidak boleh kosong")
            return v.strip()
        return v

    @field_validator('url', mode='before')
    @classmethod
    def validate_url_format(cls, v):
        if not v or not str(v).strip():
            raise ValueError("URL lampiran tidak boleh kosong")
        
        v_str = str(v)
        if not (v_str.startswith("http://") or v_str.startswith("https://")):
            raise ValueError("Format URL tidak valid. Harap gunakan format http:// atau https://")
        
        return v