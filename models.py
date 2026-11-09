from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    model_validator,
)

Name = Annotated[str, Field(min_length=1, max_length=200)]
Price = Annotated[
    StrictInt | StrictFloat, Field(ge=0, le=9_000_000, allow_inf_nan=False)
]
Quantity = Annotated[StrictInt, Field(ge=0, le=1_000_000)]


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name
    price: Price
    quantity: Quantity


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name | None = None
    price: Price | None = None
    quantity: Quantity | None = None

    @model_validator(mode="after")
    def reject_explicit_null(self) -> "ProductUpdate":
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} non può essere null")
        return self


class Product(ProductCreate):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    id: int = Field(gt=0)
