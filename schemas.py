from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)

    @field_validator("name")
    @classmethod
    def name_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("name must contain at least 2 characters")
        return value


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=0, le=120)


class UserResponse(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    price: float | None = Field(default=None, gt=0)


class ProductResponse(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderItemResponse(OrderItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    user_id: int = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    items: list[OrderItemCreate] | None = Field(default=None, min_length=1)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)
