from apps.users import current_active_user
from crud_router.router_generator import RouterGenerator
from db.db import get_async_session
from db.models.vendors import Vendor
from db.sa_crud import CRUDSA
from fastapi import Depends
from schemas.vendors import VendorSchemaOut
from schemas.vendors_base import VendorBaseSchema, VendorBaseSchemaOut

router_vendors = RouterGenerator(
    prefix='/vendors',
    schema_basic_out=VendorBaseSchemaOut,
    schema_full_out=VendorSchemaOut,
    db_crud=CRUDSA(model=Vendor),
    session=get_async_session,
    schema_create=VendorBaseSchema,
    schema_update=VendorBaseSchema,
    deps_all_routes=[Depends(current_active_user)],
    route_get_all=True,
    route_get_all_with_related=True,
    route_get_by_id=True,
    route_create=True,
    route_create_batch=True,
    route_update=True,
    route_delete=True,
)
