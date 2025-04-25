from pydantic import BaseModel, UUID4, HttpUrl
from typing import List, Optional
from datetime import datetime

class PropertyImageCreate(BaseModel):
    url: HttpUrl
    is_cover: bool

class PropertyAmenityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PropertyReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None
    reviewer_name: str

class PropertyCreate(BaseModel):
    name: str
    location: str
    price: float
    user_id: UUID4
    images: Optional[List[PropertyImageCreate]] = []
    amenities: Optional[List[PropertyAmenityCreate]] = []
    reviews: Optional[List[PropertyReviewCreate]] = []

class PropertyResponse(BaseModel):
    id: UUID4
    name: str
    location: str
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
