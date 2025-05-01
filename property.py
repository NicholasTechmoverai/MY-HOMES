import uuid
import os
from typing import List
from tortoise.transactions import in_transaction
from my_orms import Property, PropertyImage, PropertyAmenity
from schemas.property import PropertyFilter,PropertyResponse
from fastapi import UploadFile
from datetime import datetime


from  config import Config

UPLOAD_DIR = "static/files/img"


class PropertyService:
    @staticmethod
    async def save_image(file: UploadFile) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(await file.read())
        return filename

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
                state=data.state
            )

            # Save Images
            for img in images:
                img_path = await PropertyService.save_image(img)
                await PropertyImage.create(property=property_obj, image_url=img_path, is_featured=False)

            # Save Amenities
            for amenity in data.amenities:
                await PropertyAmenity.create(property=property_obj, ammenity_name=amenity, description='')

            return property_obj

    @staticmethod
    async def filter_properties(filters: PropertyFilter):
        query = Property.all().prefetch_related("images", "amenities", "reviews").select_related("owner")

        # Apply filters
        if filters.type:
            query = query.filter(property_type=filters.type)
        if filters.city:
            query = query.filter(city=filters.city)
        if filters.min_price is not None:
            query = query.filter(price__gte=filters.min_price)
        if filters.max_price is not None:
            query = query.filter(price__lte=filters.max_price)
        if filters.bedrooms is not None:
            query = query.filter(bedrooms=filters.bedrooms)
        if filters.bathrooms is not None:
            query = query.filter(bathrooms=filters.bathrooms)
        if filters.min_year is not None:
            query = query.filter(year_built__gte=filters.min_year)
        if filters.max_year is not None:
            query = query.filter(year_built__lte=filters.max_year)
        if filters.owner_id:
            query = query.filter(owner_id=filters.owner_id)
        if filters.property_id:
            query = query.filter(property_id=filters.property_id)

        properties = await query
        return await PropertyService.format_properties_responce(properties)

    @staticmethod
    async def get_all():
        properties = await Property.all().prefetch_related("images", "amenities", "reviews")
        return await PropertyService.format_properties_responce(properties)

    @staticmethod
    async def get_by_id(property_id):
        property_obj = await Property.get_or_none(property_id=property_id)\
            .prefetch_related("images", "amenities", "reviews")\
            .select_related("owner")

        if property_obj:
            result = await PropertyService.format_properties_responce([property_obj])
            return result[0]  # ✅ Just return the first item from the list

        return None


    @staticmethod
    async def delete(property_id):
        property_obj = await Property.get_or_none(property_id=property_id)
        if property_obj:
            await property_obj.delete()
            return True
        return False

    @staticmethod
    async def format_properties_responce(properties):
        result = []
        for prop in properties:
            result.append(PropertyResponse(
                property_id=str(prop.property_id),
                title=prop.title,
                description=prop.description,
                price=float(prop.price),
                city=prop.city,
                state=prop.state,
                address=prop.address,
                bedrooms=prop.bedrooms,
                bathrooms=prop.bathrooms,
                size_sqft=float(prop.size_sqft),
                year_built=prop.year_built,
                property_type=prop.property_type,
                is_verified=prop.is_verified,
                is_available=prop.is_available,
                created_at=prop.created_at.isoformat(),
                updated_at=prop.updated_at.isoformat(),
                owner_id=str(prop.owner_id),
                listing_date=prop.year_built,
                is_for_rent=False,
                contact_info={
                    'name': prop.contact_name,
                    'phone': prop.contact_phone,
                    'email': prop.contact_email
                },
                owner_info={
                    'name': prop.owner.name,
                    'phone': prop.owner.phonenumber,
                    'email': prop.owner.email,
                    'picture':f"{Config.IMAGE_PATH}/{ prop.owner.profile_picture}"
                },
                images=[{ 'url': f"/{Config.IMAGE_PATH}/{img.image_url}", 'is_featured': img.is_featured } for img in prop.images],
                is_featured=False,  # You can select this based on your logic
                amenities=[a.ammenity_name for a in prop.amenities],
                reviews=[{
                    'rating': r.rating,
                    'comment': r.comment
                } for r in prop.reviews]
            ))
        return result
