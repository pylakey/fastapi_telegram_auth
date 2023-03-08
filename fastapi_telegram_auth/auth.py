from datetime import (
    datetime,
    timedelta,
)
from enum import Enum
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    params,
    status,
)
from fastapi.datastructures import (
    Default,
    DefaultPlaceholder,
)
from fastapi.encoders import (
    DictIntStrAny,
    SetIntStr,
)
from fastapi.responses import JSONResponse
from fastapi.routing import (
    APIRoute,
    BaseRoute,
)
from fastapi.utils import generate_unique_id
from starlette.types import ASGIApp

from .types import TelegramLoginData
from .utils import validate


class TelegramAuth(APIRouter):
    def __init__(
            self,
            bot_token: str,
            on_success: Callable[[TelegramLoginData], Coroutine[Any, Any, Any]] = None,
            prefix: str = "",
            tags: Optional[List[Union[str, Enum]]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            routes: Optional[List[BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[APIRoute] = APIRoute,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
            response_model: Any = Default(None),
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                JSONResponse
            ),
    ):
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )
        self.bot_token = bot_token
        self.on_success = on_success
        self.add_api_route(
            path='',
            endpoint=self.__login_post,
            methods=['POST'],
            response_class=response_class,
            response_model=response_model,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
        )
        self.add_api_route(
            path='',
            endpoint=self.__login_get,
            methods=['GET'],
            response_class=response_class,
            response_model=response_model,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
        )

    async def __login_post(self, data: TelegramLoginData):
        return await self.__handle_login(data)

    async def __login_get(self, data: TelegramLoginData = Depends(TelegramLoginData)):
        return await self.__handle_login(data)

    async def __handle_login(self, data: TelegramLoginData):
        if not validate(data, self.bot_token):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data")

        hour_ago = datetime.utcnow() - timedelta(hours=1)

        if data.auth_date <= hour_ago.timestamp():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Outdated data")

        if callable(self.on_success):
            return await self.on_success(data)
