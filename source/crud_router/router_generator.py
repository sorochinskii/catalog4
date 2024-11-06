# from msilib import schema
import json
from collections.abc import Iterator
from enum import Enum
from typing import Any, Callable, Coroutine, Literal, Type

from db.db import get_async_session
from db.sa_crud import CRUDSA
from exceptions.http_exceptions import (
    HttpExceptionsHandler,
    HTTPObjectNotExist,
    HTTPUniqueAttrException,
)
from exceptions.sa_handler_manager import ErrorHandler, ItemNotUnique
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from loguru import logger
from pydantic.json import pydantic_encoder
from schemas.base import BaseSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


class RouterGenerator(APIRouter):
    root_path = '/'

    def __init__(
        self,
        db_crud: CRUDSA,
        schema_basic_out: Type[BaseSchema],
        schema_basic_in: Type[BaseSchema] | None = None,
        schema_in: Type[BaseSchema] | None = None,
        schema_full_out: Type[BaseSchema] | None = None,
        schema_create: Type[BaseSchema] | None = None,
        schema_update: Type[BaseSchema] | None = None,
        prefix: str | None = None,
        tags: list[str | Enum] = [],
        route_get_all: bool = False,
        route_get_all_with_related: bool = False,
        route_get_by_id: bool = False,
        route_create: bool = False,
        route_create_batch: bool = False,
        route_update: bool = False,
        route_delete: bool = False,
        deps_all_routes: list[Depends] = [],
        deps_route_get_all_related: list[Depends] = [],
        deps_route_get_all: list[Depends] = [],
        deps_route_get_by_id: list[Depends] = [],
        deps_route_create: list[Depends] = [],
        deps_route_create_batch: list[Depends] = [],
        deps_route_update: list[Depends] = [],
        deps_route_delete: list[Depends] = [],
        session: AsyncSession = get_async_session,
        *args, **kwargs
    ) -> None:
        self.db_crud = db_crud
        self.schema_basic_in = schema_basic_in
        self.schema_basic_out = schema_basic_out
        self.schema_in = schema_in
        self.schema_full_out = schema_full_out
        self.schema_create = schema_create
        self.schema_update = schema_update
        self.session = session

        prefix = str(prefix if prefix else self.schema.__name__).lower()
        prefix = self.root_path + prefix.strip("/")
        tags = tags or [prefix.strip("/")]

        super().__init__(prefix=prefix, tags=tags, )

        if route_get_all:
            self._add_api_route(
                '',
                endpoint=self._get_all(self.schema_basic_out),
                methods=["GET"],
                response_model=list[self.schema_basic_out] | None,
                summary="Get all",
                dependencies=deps_route_get_all + deps_all_routes)

        if route_get_all_with_related:
            self._add_api_route(
                '/related/',
                endpoint=self._get_all_with_related(
                    schema=self.schema_full_out),
                methods=["GET"],
                response_model=list[self.schema_full_out] | None,
                summary="Get all with related",
                dependencies=deps_route_get_all_related + deps_all_routes)

        if route_get_by_id:
            self._add_api_route(
                '/{item_id}/',
                endpoint=self._get_by_id(schema=self.schema_basic_out),
                methods=["GET"],
                response_model=self.schema_basic_out,
                summary="Get by id",
                dependencies=deps_route_get_by_id + deps_all_routes)

        if route_create:
            self._add_api_route(
                '',
                endpoint=self._create(
                    schema_create=self.schema_create,
                    schema_out=self.schema_basic_out),
                methods=["POST"],
                response_model=self.schema_basic_out,
                summary="Create",
                dependencies=deps_route_create + deps_all_routes)

        if route_update:
            self._add_api_route(
                '/{item_id}/',
                endpoint=self._update(self.schema_update,
                                      schema_out=self.schema_basic_out),
                methods=["PATCH"],
                response_model=self.schema_basic_out,
                summary="Update",
                dependencies=deps_route_update + deps_all_routes)

        if route_delete:
            self._add_api_route(
                '/{item_id}/',
                endpoint=self._delete(),
                methods=["DELETE"],
                response_model=self.schema_in,
                summary="Delete item",
                dependencies=deps_route_delete + deps_all_routes)

        if route_create_batch:
            self._add_api_route(
                '/batch/',
                endpoint=self._create_batch(
                    schema_create=self.schema_create,
                    schema_out=list[Any | str]),
                methods=["POST"],
                # self.self.schema_basic_out),
                response_model=list[self.schema_basic_out | str],
                summary="Create batch",
                dependencies=deps_route_create_batch + deps_all_routes)

    def _add_api_route(
        self,
        path,
        endpoint: Callable[..., Any],
        dependencies: list[Depends] = [],
        error_responses: list[HTTPException] | None = None,
        **kwargs: Any,
    ) -> None:
        super().add_api_route(
            path, endpoint, dependencies=dependencies,
            ** kwargs
        )

    def _get_all(self, schema: BaseSchema) -> Callable:
        async def endpoint(session: AsyncSession = Depends(self.session)):
            include_fields = schema.model_fields
            with ErrorHandler() as error_handler:
                models = await self.db_crud.get_all(session, include_fields)
            return models
        return endpoint

    def _get_all_with_related(self, schema: BaseSchema) -> Callable:
        async def endpoint(session: AsyncSession = Depends(self.session)):
            stmt = select(self.db_crud.model
                          ).order_by(
                getattr(self.db_crud.model, self.db_crud.model.get_pks()[0]))
            with ErrorHandler() as error_handler:
                models = await session.scalars(stmt)
            result = models.unique().all()
            return result
        return endpoint

    def _get_by_id(self, schema: BaseSchema) -> Coroutine:
        async def endpoint(item_id: int,
                           session: AsyncSession = Depends(self.session)):
            include_fields = schema.model_fields
            with HttpExceptionsHandler():
                result = await self.db_crud.get_by_id(item_id,
                                                      include=include_fields,
                                                      session=session)
            return result
        return endpoint

    def _create(self,
                schema_create: BaseSchema,
                schema_out: BaseSchema) -> Coroutine:
        async def endpoint(data: schema_create = Body(),
                           session: AsyncSession = Depends(self.session)
                           ) -> schema_out:
            try:
                logger.debug('Create endpoint. Data', data.dict())
                response: int = await self.db_crud.create(
                    data=data.dict(), session=session)
                return response
            except ItemNotUnique:
                raise HTTPUniqueAttrException
        return endpoint

    def _create_batch(self,
                      schema_create: BaseSchema,
                      schema_out: BaseSchema) -> Coroutine:
        async def endpoint(data: list[schema_create] = Body(),
                           session: AsyncSession = Depends(self.session)
                           ) -> list[schema_out | str]:
            data = [item.dict() for item in data]
            logger.debug('Create endpoint. Data', data)
            response: list[BaseSchema] = await self.db_crud.create_batch(
                data=data, session=session)
            return response
        return endpoint

    def _update(self, schema: BaseSchema, schema_out: BaseSchema) -> Coroutine:

        async def endpoint(item_id: int,
                           session: AsyncSession = Depends(self.session),
                           data: schema = Body()
                           ) -> self.schema_basic_out:
            data = jsonable_encoder(data)
            item_id = await self.db_crud.update(item_id, data, session)
            if not item_id:
                raise HTTPObjectNotExist
            result = await self.db_crud.get_by_id(item_id, session=session)
            return result

        return endpoint

    def _delete(self) -> Coroutine:
        async def endpoint(item_id: int,
                           session: AsyncSession = Depends(self.session)
                           ) -> int | None:
            with HttpExceptionsHandler():
                result = await self.db_crud.delete(item_id, session)
            return result
        return endpoint
