from device_base import DeviceBaseSchemaOut
from schemas.vendors_base import VendorBaseSchema


class VendorSchema(VendorBaseSchema):
    ...


class VendorSchemaOut(VendorSchema):
    id: int
    devices: list[DeviceBaseSchemaOut]
