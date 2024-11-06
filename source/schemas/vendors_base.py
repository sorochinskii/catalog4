from schemas.base import BaseSchema


class VendorBaseSchema(BaseSchema):
    name: str


class VendorBaseSchemaOut(VendorBaseSchema):
    id: int

    class Config:
        from_attributes = True
