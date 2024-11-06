from dataclasses import dataclass
from typing import Any, Sequence, Type

from db.models.base import BaseCommon
from exceptions.sa_handler_manager import ErrorHandler
from loguru import logger
from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, raiseload

MODEL_TYPE = Type[BaseCommon]


class CRUDSA:
    '''
        This class definition is for a CRUD (Create, Read, Update, Delete) operations interface for a SQLAlchemy database model. Here's a brief explanation of what each method does:

        init: Initializes the CRUD interface with a database model.
        SelectOptions: A dataclass to hold select options for database queries.
        get_all: Retrieves all records from the database model.
        get_all_with_related: Retrieves all records from the database model, including related records.
        get_by_id: Retrieves a record from the database model by its ID.
        get_with_filters: Retrieves records from the database model based on filter criteria.
        create: Creates a new record in the database model.
        create_batch: Creates multiple new records in the database model.
        update: Updates an existing record in the database model.
        delete: Deletes a record from the database model.
        delete_batch: Deletes multiple records from the database model.
        check_exist_by_id: Checks if a record exists in the database model by 
        its ID.
        _get_select_options: Helper method to generate select options for 
        database queries.
        get_model: Returns the database model associated with the CRUD 
        interface.
    '''

    def __init__(
            self,
            model: MODEL_TYPE,
            *args: Any,
            **kwargs: Any
    ):
        self.model = model

    @dataclass
    class SelectOptions:
        raiseload: list[Any]
        load_only: Any

    async def get_all(self,
                      session: AsyncSession,
                      include: list[Any] = [],
                      exclude: list[Any] = []) -> Sequence[Any]:
        options = self._get_select_options(include, exclude)
        stmt = select(self.model
                      ).options(*options.raiseload, options.load_only)
        async with session as session:
            with ErrorHandler() as error_handler:
                raw = await session.scalars(stmt)
                result = raw.unique().all()
        return result

    async def get_all_with_related(self,
                                   session: AsyncSession,
                                   include: list[Any] = [],
                                   exclude: list[Any] = []) -> Sequence[Any]:
        options = self._get_select_options(include, exclude)

        stmt = select(self.model
                      ).order_by(
            getattr(self.model, self.model.get_pks()[0])).options(*options.raiseload, options.load_only)
        async with session as session:
            with ErrorHandler() as error_handler:
                raw = await session.scalars(stmt)
                result = raw.unique().all()
        return result

    async def get_by_id(self,
                        id: int,
                        session: AsyncSession,
                        include: list[Any] = [],
                        exclude: list[Any] = []) -> Any:
        options = self._get_select_options(include, exclude)
        stmt = select(self.model
                      ).options(*options.raiseload, options.load_only
                                ).filter_by(id=id)
        async with session as session:
            with ErrorHandler() as error_handler:
                result = await session.execute(stmt)
                item = result.unique().one()[0]
        return item

    async def get_with_filters(self,
                               session: AsyncSession,
                               include: list[Any] = [],
                               exclude: list[Any] = [],
                               **filters) -> Any:
        # filters = kwargs.get('filters')
        options = self._get_select_options(include, exclude)
        stmt = select(self.model
                      ).options(*options.raiseload, options.load_only
                                ).filter_by(**filters)
        async with session:
            with ErrorHandler() as error_handler:
                result = await session.execute(stmt)
                item = result.one()[0]
        return item

    async def create(self,
                     data: dict,
                     session: AsyncSession) -> Any:
        stmt = insert(self.model).returning(self.model)
        async with session:
            with ErrorHandler():
                result = await session.scalar(stmt, [data])
                await session.commit()
        logger.debug(f"SA crud create statement: {stmt}, data: {data}")
        return result

    async def create_batch(self,
                           data: list[dict],
                           session: AsyncSession) -> Any:
        result_batch = list()
        for item in data:
            try:
                result = await self.create(item, session)
            except Exception as e:
                result_batch.append('error')
            else:
                result_batch.append(result)
        return result_batch

    async def update(self, id: int,
                     data: dict,
                     session: AsyncSession,
                     include: list[Any] = [],
                     exclude: list[Any] = []) -> int | None:
        stmt = update(self.model).\
            where(self.model.id == id).\
            values(data).\
            returning(self.model.id)
        async with session:
            item_id = await session.scalar(stmt)
            await session.commit()
        return item_id

    async def delete(self, item_id: int, session: AsyncSession) -> int | None:
        stmt = delete(self.model).\
            where(self.model.id == item_id).\
            returning(self.model.id)
        with ErrorHandler():
            await self.check_exist_by_id(item_id, session)
        async with session:
            result = await session.scalar(stmt)
            await session.commit()
        return result

    async def delete_batch(self, ids: list[int],
                           session: AsyncSession) -> None:
        stmt = delete(self.model).\
            where(self.model.id.in_(ids))
        async with session:
            await session.scalar(stmt)
            await session.commit()

    async def check_exist_by_id(self, id, session):
        query = text(
            f'SELECT * FROM {self.model.__tablename__} WHERE id=:id')
        async with session:
            result = await session.execute(query, {'id': id})
        return result.one()

    def _get_select_options(self,
                            include: list[Any] = [],
                            exclude: list[Any] = [],
                            raise_all_relations: bool = True
                            ) -> SelectOptions:
        '''
            If field defined in both exclude and include lists,
                excluding priority
            higher than including. (i.e. excluding more powerful.)
            If any relation included to include list
                and raise_all_relations == True, then all relations raised.
            If include list empty, its equal that all fields included to it.
            If at least one field/relation defined in include list,
                other fields/relations excluded.
            If at least one field/relation defined in exclude list,
                other fields/relations included.
        '''
        model_fields = self.model.as_list()
        pks = self.model.get_pks()
        fks = self.model.get_fks()
        relationships = self.model.get_relationships()
        if relationships:
            raise_all_relations = False
        select_options = self.SelectOptions(raiseload=[], load_only=[])
        if include:
            clean_include = [field for field in include
                             if field not in exclude]
            include = clean_include
        elif not include:
            include = [field for field in model_fields
                       if field not in exclude]
        include_list = [field for field in model_fields if (
            field in include
            and field not in exclude
            # and field not in pks
            and field not in fks)]
        include_fields = []
        for field in include_list:
            attr = getattr(self.model, field, None)
            if attr:
                include_fields.append(attr)
        select_options.load_only = load_only(*include_fields)
        if not raise_all_relations:
            for relation in relationships:
                if ((attr := getattr(self.model, relation, False))
                        and (relation in exclude or relation not in include)):
                    select_options.raiseload.append(raiseload(attr))
        else:
            select_options.raiseload.append(raiseload('*'))
        return select_options

    def get_model(self) -> Type[BaseCommon]:
        return self.model
