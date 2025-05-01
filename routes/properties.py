from fastapi import APIRouter, HTTPException, UploadFile, File, Form ,Body,Request
from schemas.property import PropertyCreate, PropertyResponse,PropertyFilter,PropertyListResponse
from property import PropertyService  # Assuming this is your service layer
from typing import List
from uuid import UUID
from fastapi.templating import Jinja2Templates

property_router = APIRouter(tags=["Properties"])

from fastapi import APIRouter, Form, File, UploadFile
from typing import List
from uuid import UUID

from fastapi import Request
from fastapi.responses import HTMLResponse

from typing import Optional
from pydantic import BaseModel


@property_router.post("/sell")
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
        state= state,
    )

    new_property = await PropertyService.create(property_data, images)
    return {"status": "success", "property_id": new_property.property_id}

from fastapi import Query


@property_router.post("/", response_model=PropertyListResponse)
async def list_properties(
    filters: PropertyFilter = Body(...),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = await PropertyService.filter_properties(filters)
    # print(type(query))
    # print(query)

    results = query

    return {
        "success": True,
        "properties": results,  
        "meta": {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "returned": len(results)
        }
    }

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@property_router.get("/{property_id}", response_model=PropertyListResponse)
async def get_property(property_id: UUID, request: Request):
    prop = await PropertyService.get_by_id(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return templates.TemplateResponse("indetails.html",context={"request": request, "details": prop})
    # return prop




@property_router.delete("/{property_id}")
async def delete_property(property_id: UUID):
    success = await PropertyService.delete(property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Deleted successfully"}
