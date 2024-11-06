from datetime import datetime

from schemas.base import BaseSchema


class DeviceBaseSchema(BaseSchema):
    serial: str
    name: str | None = None
    responsible_person_id: int | None = None
    room_id: int | None = None
    vendor_id: int | None = None


class DeviceBaseSchemaOut(DeviceBaseSchema):
    id: int


class DeviceBaseSchemaIn(DeviceBaseSchema):
    ...


class MFPBaseSchemaOut(DeviceBaseSchema):
    id: int
    created: datetime
    updated: datetime
