import asyncio
from tortoise.expressions import Q
from my_orms import User, Property, PropertyImage, PropertyAmenity, PropertyReview
from typing import Optional, Dict
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, EmailStr, constr

from tortoise.exceptions import DoesNotExist

class UserHandler:
    def __init__(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.location = location

    def validate_user_data(self) -> Dict:
        if not (self.username and self.email and self.password):
            return {"success": False, "message": "Username, email, and password are required."}
        return {"success": True}

    @staticmethod
    async def fetch_user_by_email(email: str) -> Optional[User]:
        try:
            return await User.get(email=email)
        except DoesNotExist:
            return None

    async def login(self) -> Dict:
        if not self.email or not self.password:
            return {"success": False, "message": "Email and password are required."}

        try:
            user = await self.fetch_user_by_email(self.email)
            if user and check_password_hash(user.password, self.password):
                return {
                    "success": True,
                    "user_info": await self.fetch_user(),  # Assuming fetch_user fetches the current user's info
                    "message": "Login successful."
                }
            return {"success": False, "message": "Invalid email or password."}
        except Exception as err:
            return {"success": False, "message": f"Login failed: {str(err)}"}

    async def create_user(self) -> Dict:
        # Validate inputs
        validation_result = self.validate_user_data()
        if not validation_result["success"]:
            return validation_result

        try:
            user = await User.create(
                name=self.username,
                email=self.email,
                password=generate_password_hash(self.password),
                phonenumber=self.phone,
                location=self.location
            )
            return {
                "success": True,
                "user_id": str(user.user_id),
                "message": "User created successfully."
            }
        except Exception as err:
            return {"success": False, "message": f"Error creating user: {str(err)}"}

    async def fetch_user(self) -> Dict:
        if not self.user_id and not self.email:
            return {"success": False, "message": "User ID or email is required."}

        try:
            query = Q()
            if self.user_id:
                query |= Q(user_id=self.user_id)
            if self.email:
                query |= Q(email=self.email)

            user = await User.get(query)
            return user.to_dict() if user else {"success": False, "message": "User not found."}

        except DoesNotExist:
            return {"success": False, "message": "User not found."}
        except Exception as err:
            return {"success": False, "message": f"Error fetching user: {str(err)}"}

    async def update_user(self) -> Dict:
        if not self.user_id:
            return {"success": False, "message": "User ID is required to update."}

        try:
            user = await User.get(user_id=self.user_id)

            updated = False
            if self.username:
                user.name = self.username
                updated = True
            if self.email:
                user.email = self.email
                updated = True
            if self.phone:
                user.phonenumber = self.phone
                updated = True
            if self.password:
                user.password = generate_password_hash(self.password)
                updated = True
            if self.location:
                user.location = self.location
                updated = True

            if not updated:
                return {"success": False, "message": "No updates provided."}

            await user.save()
            return {"success": True, "message": "User updated successfully."}

        except DoesNotExist:
            return {"success": False, "message": "User not found."}
        except Exception as err:
            return {"success": False, "message": f"Error updating user: {str(err)}"}


