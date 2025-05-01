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

from pydantic import BaseModel
from typing import List, Optional

class ContactInfo(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]

class OwnerInfo(BaseModel):
    name: str
    phone: str
    email: str
    picture: Optional[str]

class PropertyImaged(BaseModel):
    url: str
    is_featured: bool
 

class PropertyResponse(BaseModel):
    property_id: str
    title: str
    description: str
    price: float
    city: str
    state: str
    address: str
    bedrooms: int
    bathrooms: int
    size_sqft: float
    year_built: int
    property_type: str
    is_verified: bool
    is_available: bool
    created_at: str
    updated_at: str
    owner_id: str
    listing_date: int
    is_for_rent: bool
    contact_info: ContactInfo
    owner_info: OwnerInfo
    images: List[PropertyImaged]
    is_featured: bool
    amenities: List[str]
    reviews: List[dict]  # If reviews have a specific structure, replace dict with that model

    class Config:
        orm_mode = True  # This allows Pydantic to parse ORM models

class Meta(BaseModel):
    total: int
    limit: int
    offset: int
    returned: int

class PropertyListResponse(BaseModel):
    success: bool
    properties: List[PropertyResponse]
    meta: Meta

class PropertyFilter(BaseModel):
    type: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    city: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    owner_id: Optional[UUID] = None
    property_id: Optional[UUID] = None