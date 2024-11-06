from typing import TYPE_CHECKING

from db.models.base import BaseCommon
from db.models.devices import Device, PolymorphicMixin
from db.models.vendors import Vendor
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Self

if TYPE_CHECKING:
    from db.models.vendors import Vendor


class Model(BaseCommon):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    vendor_id: Mapped[int | None] = mapped_column(
        ForeignKey('vendor.id'))
    vendor: Mapped[Vendor] = relationship(
        back_populates='cartridge_models', foreign_keys=[vendor_id])
    is_original: Mapped[bool] = False
    original_id: Mapped[int | None] = mapped_column(
        ForeignKey('model.id'))
    alternatives: Mapped[Self | None] = relationship(
        'Model', remote_side=original_id)
    cartridges: Mapped[list['Cartridge']] = relationship(
        back_populates='model')


class Cartridge(Device, PolymorphicMixin):
    id: Mapped[int] = mapped_column(ForeignKey('device.id'), primary_key=True)

    model_id: Mapped[int | None] = mapped_column(ForeignKey('model.id'))
    model: Mapped['Model'] = relationship(
        back_populates='cartridges', foreign_keys=[model_id])
