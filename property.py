from my_orms import Property, PropertyImage, PropertyAmenity, PropertyReview
from schemas.property import PropertyCreate
from tortoise.transactions import in_transaction

class PropertyService:
    @staticmethod
    async def create(data: PropertyCreate):
        async with in_transaction():
            property_obj = await Property.create(
                name=data.name,
                location=data.location,
                price=data.price,
                user_id=data.user_id
            )

            if data.images:
                await PropertyImage.bulk_create([
                    PropertyImage(property=property_obj, **image.dict()) for image in data.images
                ])

            if data.amenities:
                await PropertyAmenity.bulk_create([
                    PropertyAmenity(property=property_obj, **amenity.dict()) for amenity in data.amenities
                ])

            if data.reviews:
                await PropertyReview.bulk_create([
                    PropertyReview(property=property_obj, **review.dict()) for review in data.reviews
                ])

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
