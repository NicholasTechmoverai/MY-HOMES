from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from schemas.property import PropertyCreate, PropertyResponse,PropertyFilter
from property import PropertyService  # Assuming this is your service layer
from typing import List
from uuid import UUID

property_router = APIRouter(tags=["Properties"])

from fastapi import APIRouter, Form, File, UploadFile
from typing import List
from uuid import UUID

from fastapi import Request

from typing import Optional
from pydantic import BaseModel


@property_router.post("/")
async def create_property(
    request: Request,
    title: str = Form(...),
    type: str = Form(...),  # Must match frontend 'type'
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    price: float = Form(...),
    size: float = Form(...),  # Must match frontend 'size'
    bedrooms: int = Form(None),
    bathrooms: int = Form(None),
    year: int = Form(None),  # Must match frontend 'year'
    description: str = Form(...),
    contact_name: str = Form(None),
    contact_phone: str = Form(None),
    contact_email: str = Form(None),
    owner_id: str = Form(...),
    images: List[UploadFile] = File(...),
):
    form_data = await request.form()
    amenities = form_data.getlist("amenities")  # Ensure 'amenities' is the correct field name

    try:
        owner_uuid = UUID(owner_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid owner_id format")

    # Debug: Print all received form data
    print("=== Received Form Data ===")
    for key, value in form_data.multi_items():
        print(f"{key}: {value}")

    # Create Property
    property_data = PropertyCreate(
        title=title,
        type=type,
        address=address,
        city=city,
        price=price,
        size=size,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        year=year,
        description=description,
        amenities=amenities,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        owner_id=owner_uuid,
        state= "Naks",
    )

    new_property = await PropertyService.create(property_data, images)
    return {"status": "success", "property_id": new_property.property_id}
@property_router.get("/", response_model=PropertyFilter)
async def list_properties():
    return await PropertyService.get_all()

@property_router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: UUID):
    prop = await PropertyService.get_by_id(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop

@property_router.delete("/{property_id}")
async def delete_property(property_id: UUID):
    success = await PropertyService.delete(property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Deleted successfully"}
