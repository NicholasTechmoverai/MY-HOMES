from fastapi import APIRouter, HTTPException
from schemas.normals import LoginInput,createUser
from users import UserHandler

main_router = APIRouter()

@main_router.post('/login/email')
async def email_login(credentials: LoginInput):
    user_handler = UserHandler(email=credentials.email, password=credentials.password)
    result = await user_handler.login()

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {"success": True, "message": result["message"], "user_info": result.get("user_info")}


@main_router.post('/create')
async def create_user_route(data: createUser):
    handler = UserHandler(
        username=data.name,
        email=data.email,
        password=data.password,
        phone=data.phone_number,
        location=""
    )
    result = await handler.create_user()
    return result
