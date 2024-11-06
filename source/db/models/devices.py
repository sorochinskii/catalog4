import datetime
from typing import TYPE_CHECKING

from db.models.base import BaseCommon
from db.models.persons import Person
from db.models.utils import split_and_concatenate
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.ext.declarative import AbstractConcreteBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from source.apps.vendors.models import Vendor

if TYPE_CHECKING:
    from db.models.rooms import Room
    from db.models.vendors import Vendor


class NetworkDeviceMixin:
    mac: Mapped[str] = mapped_column(nullable=True)


class PolymorphicMixin:
    @declared_attr.directive
    def __mapper_args__(cls):
        return {
            'polymorphic_identity': lambda: split_and_concatenate(cls.__name__)
        }


class Device(BaseCommon):
    serial: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str | None]
    type: Mapped[str]
    created = mapped_column(DateTime(timezone=True),
                            server_default=func.now(), nullable=False)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey('vendor.id'))
    vendor: Mapped['Vendor'] = relationship(
        back_populates='devices')

    @declared_attr.directive
    def __mapper_args__(cls):
        return {
            'polymorphic_on': 'type',
            'polymorphic_identity': split_and_concatenate(cls.__name__)
        }
