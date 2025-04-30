from pydantic import BaseModel, EmailStr

class LoginInput(BaseModel):
    # email: EmailStr
    email: str
    password: str
