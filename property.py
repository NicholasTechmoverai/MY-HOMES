import uuid
import os
from typing import List
from tortoise.transactions import in_transaction
from my_orms import Property, PropertyImage, PropertyAmenity
from fastapi import UploadFile
from datetime import datetime

UPLOAD_DIR = "statics/fies/img"

class PropertyService:
    @staticmethod
    async def save_image(file: UploadFile) -> str:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(await file.read())
        return filepath

    @staticmethod
    async def create(data, images: List[UploadFile]):
        async with in_transaction():
            property_obj = await Property.create(
                title=data.title,
                property_type=data.type,
                description=data.description,
                price=data.price,
                address=data.address,
                city=data.city,
                size_sqft=data.size,
                bedrooms=data.bedrooms,
                bathrooms=data.bathrooms,
                year_built=data.year,
                owner_id=data.owner_id,
                state = data.state
            )

            # Save Images
            for img in images:
                img_path = await PropertyService.save_image(img)
                await PropertyImage.create(property=property_obj, image_url=img_path)

            # Save Amenities
            for amenity in data.amenities:
                await PropertyAmenity.create(property=property_obj, ammenity_name=amenity)

            return property_obj


    @staticmethod
    async def get_all():
        return await Property.all().prefetch_related("images", "amenities", "reviews")

    @staticmethod
    async def get_by_id(property_id):
        return await Property.get_or_none(id=property_id).prefetch_related("images", "amenities", "reviews")

    @staticmethod
    async def delete(property_id):
        property_obj = await Property.get_or_none(id=property_id)
        if property_obj:
            await property_obj.delete()
            return True
        return False
