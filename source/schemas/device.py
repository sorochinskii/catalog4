from datetime import datetime

from schemas.device_base import DeviceBaseSchemaOut
from schemas.person_base import PersonBaseSchemaOut
from schemas.rooms_base import RoomBaseSchemaOut
from schemas.vendors_base import VendorBaseSchemaOut


class DeviceSchemaOut(DeviceBaseSchemaOut):
    responsible_person: PersonBaseSchemaOut
    room: RoomBaseSchemaOut
    vendor: VendorBaseSchemaOut
    created: datetime
