from pydantic import BaseModel, UUID4, HttpUrl, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class PropertyImageCreate(BaseModel):
    url: HttpUrl
    is_cover: Optional[bool] = False


class PropertyAmenityCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PropertyReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None
    reviewer_name: str


class PropertyCreate(BaseModel):
    title: str
    type: str
    address: str
    city: str
    state:str
    price: float
    size: float
    bedrooms: int
    bathrooms: int
    year: int
    description: str
    amenities: List[str]
    contact_name: str
    contact_phone: str
    contact_email: str
    owner_id: UUID

class PropertyResponse(BaseModel):
    id: UUID4
    name: str
    type: str
    address: str
    city: str
    location: str
    size: int
    bedrooms: int
    bathrooms: int
    year: int
    description: Optional[str]
    price: float
    contact_name: str
    contact_phone: str
    contact_email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PropertyFilter(BaseModel):
    type: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    city: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    owner_id: Optional[str] = None
    property_id: Optional[str] = None