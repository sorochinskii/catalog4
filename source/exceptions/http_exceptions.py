from exceptions.sa_handler_manager import ItemNotFound, ItemNotUnique
from fastapi import HTTPException, status
from fastapi_users import exceptions as fast_users_exceptions
from fastapi_users.exceptions import UserNotExists
from fastapi_users.router.common import ErrorCode as FastUsersErrorCode
from loguru import logger

HTTPObjectNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found."
)

HTTPUniqueAttrException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Unique attribute exists."
)

HTTPUniqueException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Unique item exists."
)

HTTPUserNotExists = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not exists."
)


HTTPVerifyBadToken = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=FastUsersErrorCode.VERIFY_USER_BAD_TOKEN,
)

HTTPUserAlreadyVerified = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=FastUsersErrorCode.VERIFY_USER_ALREADY_VERIFIED,
)


class HttpExceptionsHandler:
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_instance, traceback):
        match ex_instance:
            case ItemNotUnique():
                raise HTTPUniqueException
            case ItemNotFound():
                raise HTTPObjectNotExist
            case UserNotExists():
                raise HTTPUserNotExists
            case fast_users_exceptions.InvalidVerifyToken():
                raise HTTPVerifyBadToken
            case fast_users_exceptions.UserAlreadyVerified():
                raise HTTPUserAlreadyVerified
        if ex_instance:
            logger.error(f"Inside HttpExceptionsHandler {ex_instance}")
            raise ex_instance
