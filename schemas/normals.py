from pydantic import BaseModel, EmailStr

class LoginInput(BaseModel):
    # email: EmailStr
    email: str
    password: str


class createUser(BaseModel):
    email:str
    name:str
    password:str
    # picture:str
    phone_number:str