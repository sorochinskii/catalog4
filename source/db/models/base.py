from datetime import datetime
from typing import Annotated, Any

from db.models.utils import split_and_concatenate
from sqlalchemy import func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    ...


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        try:
            if (not cls.__mapper_args__.get('polymorphic_abstract')
                    and (cls.__mapper_args__.get('polymorphic_identity') and cls.__mapper_args__.get('polymorphic_on'))):
                return split_and_concatenate(cls.__name__)
        except AttributeError:
            return split_and_concatenate(cls.__name__)


class BaseCommon(Base, TableNameMixin):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}

    @ classmethod
    def tablename(cls):
        return cls.__tablename__

    @ classmethod
    def as_list(cls) -> list[Any]:
        '''
        Return list of model fields stringed names except pki fields.
        '''
        result = []
        for c in inspect(cls).mapper.column_attrs:
            result.append(c.key)
        return result

    @ classmethod
    def get_relationships(cls) -> list[Any]:
        '''
        Return list of model relations.
        '''
        result = []
        for c in inspect(cls).mapper.relationships:
            result.append(c.key)
        return result

    @ classmethod
    def get_pks(cls) -> list[Any]:
        '''
        Return list of primary keys.
        '''
        result = []
        for pk in inspect(cls).primary_key:
            result.append(pk.name)
        return result

    @ classmethod
    def get_fks(cls) -> list[Any]:
        '''
        Return list of foreign keys.
        '''
        result = []
        mapper = inspect(cls)
        for column in mapper.columns:
            if column.foreign_keys:
                result.append(column.key)
        return result

    class Config:
        from_attributes = True


class BaseCommonWithoutID(Base, TableNameMixin):
    __abstract__ = True


created_at = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.now())
]


updated_at = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.now(),
                  onupdate=func.now())
]
