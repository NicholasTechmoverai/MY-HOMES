from fastapi import APIRouter, HTTPException
from schemas.property import PropertyCreate, PropertyResponse
from property import PropertyService
from typing import List
from uuid import UUID

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.post("/", response_model=PropertyResponse)
async def create_property(data: PropertyCreate):
    try:
        created = await PropertyService.create(data)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[PropertyResponse])
async def list_properties():
    return await PropertyService.get_all()

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: UUID):
    prop = await PropertyService.get_by_id(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop

@router.delete("/{property_id}")
async def delete_property(property_id: UUID):
    success = await PropertyService.delete(property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Deleted successfully"}
