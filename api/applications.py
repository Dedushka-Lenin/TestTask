from typing import Callable
from starlette import Starlette, Any
from api.routing import APIRouter
 
class FastApi(Starlette):
    def __init__(
        self,
        version: str = "0.1.0"
    ) -> None:
        self.version = version
    def get(
        self,
        path: str,
    ) -> Callable[..., Any]:
        return self.router.get(path)
    def post(
        self,
        path: str,
    ) -> Callable[..., Any]:
        return self.router.post(path)
    
    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await super().__call__(scope, receive, send)