from typing import TYPE_CHECKING

from db.models.base import BaseCommon
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.cartridges import Model
    from db.models.devices import Device


class Vendor(BaseCommon):

    name: Mapped[str] = mapped_column(unique=True, index=True)
    devices: Mapped[list['Device']] = relationship(
        back_populates='vendor', lazy='selectin')
    cartridge_models: Mapped[list['Model']
                             ] = relationship(back_populates="vendor")
