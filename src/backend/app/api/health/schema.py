from pydantic import BaseModel

class HealthData(BaseModel):
    status: str
    message: str

class ReadinessData(BaseModel):
    status: str
    database: str
    redis: str