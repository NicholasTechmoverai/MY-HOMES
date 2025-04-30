from fastapi import APIRouter, HTTPException
from schemas.normals import LoginInput
from users import UserHandler

main_router = APIRouter()

@main_router.post('/login/email')
async def email_login(credentials: LoginInput):
    user_handler = UserHandler(email=credentials.email, password=credentials.password)
    result = await user_handler.login()

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {"success": True, "message": result["message"], "user_info": result.get("user_info")}
