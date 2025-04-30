from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

from config import Config

class User(Model):
    user_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=500)
    phonenumber = fields.CharField(max_length=20, null=True)
    location = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    profile_picture = fields.CharField(max_length=255, null=True)
    is_verified = fields.BooleanField(default=False)


    def to_dict(self):
        return {
            "id": str(self.user_id),
            "name": self.name,
            "email": self.email,
            "phonenumber": self.phonenumber,
            "location": self.location,
            "picture":f"{Config.IMAGE_PATH}/{self.profile_picture}",
        }



class Property(Model):
    property_id = fields.UUIDField(pk=True)
    owner = fields.ForeignKeyField("models.User", related_name="properties")
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=20, decimal_places=2)
    address = fields.CharField(max_length=255)
    city = fields.CharField(max_length=100)
    state = fields.CharField(max_length=100,null=True)
    property_type = fields.CharField(max_length=50)  # e.g., "Apartment", "House"
    size_sqft = fields.DecimalField(max_digits=10, decimal_places=2, null=True)  # Size in square feet
    bedrooms = fields.IntField(null=True) 
    bathrooms = fields.IntField(null=True)
    garage = fields.IntField(null=True)  # Number of garage spaces
    year_built = fields.IntField(null=True)  # Year the property was built
    contact_name = fields.CharField(max_length=100, null=True)
    contact_phone = fields.CharField(max_length=20, null=True)
    contact_email = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_available = fields.BooleanField(default=True)  # Availability status
    is_verified = fields.BooleanField(default=False)  # Verification status
    

class PropertyImage(Model):
    image_id = fields.IntField(pk=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="images")
    image_url = fields.CharField(max_length=255)  # URL of the image
    uploaded_at = fields.DatetimeField(auto_now_add=True)
    is_featured = fields.BooleanField(default=False)  # Whether this image is featured
    inserted_at = fields.DatetimeField(auto_now_add=True)  # Timestamp when the image was inserted

class PropertyAmenity(Model):
    ammenity_id = fields.IntField(pk=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="ammenities")
    ammenity_name = fields.CharField(max_length=255)  # Name of the amenity (e.g., "Pool", "Gym")
    description = fields.TextField(null=True)  # Description of the amenity
    created_at = fields.DatetimeField(auto_now_add=True)

class PropertyReview(Model):
    review_id = fields.IntField(pk=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="reviews")
    user_id = fields.ForeignKeyField("models.User", related_name="reviews")
    rating = fields.IntField()  # Rating out of 5
    comment = fields.TextField(null=True)  # Review comment
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Videos(Model):
    video_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="videos")
    video_title = fields.CharField(max_length=255) 
    video_description = fields.TextField(null=True)
    video_url = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="videos")    


class Favorite(Model):
    favorite_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="favorites")
    property_id = fields.ForeignKeyField("models.Property", related_name="favorites")
    created_at = fields.DatetimeField(auto_now_add=True)

class Comments(Model):
    comment_id = fields.IntField(pk=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="comments")
    user_id = fields.ForeignKeyField("models.User", related_name="comments")
    comment = fields.TextField(null=True)  # Comment text
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)



class likes(Model):
    like_id = fields.IntField(pk=True)
    property_id = fields.ForeignKeyField("models.Property", related_name="likes")
    user_id = fields.ForeignKeyField("models.User", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)        




# async def init():
#     await Tortoise.init(
#         db_url='mysql://root:0000@localhost/MY_HOMES',
#         modules={'models': ['__main__']}  # or your app's path
#     )
#     await Tortoise.generate_schemas()  # ← This creates the tables for you!

# run_async(init())




from tortoise.contrib.fastapi import register_tortoise

def init_db(app):
    register_tortoise(
        app,
        db_url="mysql://root:0000@localhost/MY_HOMES",
        modules={"models": ["my_orms"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
