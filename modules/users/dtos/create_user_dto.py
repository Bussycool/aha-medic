from pydantic import BaseModel, Field
from modules.users.enums.role_enum import Role

class CreateUserDto(BaseModel):
  name: str = Field(..., description="Name of the user")
  email: str = Field(..., description="Email of the user")
  password: str = Field(..., description="Password of the user")
  role: Role

