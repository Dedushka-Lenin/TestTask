from typing import Callable
from starlette.routing import Router, Any
 
class APIRouter(Router):
    def __init__(self) -> None:
        super().__init__()
        self.route_class = ApiRoute

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
	  method: str
) -> None:
	route = self.route_class(
    path, 
    endpoint=endpoint, 
    method=method
)
	self.routes.append(route)

    def get(self, path: str) -> Callable[[Callable[..., Any]], [Callable[..., Any]]:
        def decorator(func: [Callable[..., Any]) -> [Callable[..., Any]:
	      self.add_api_route(path, func, method=”get”)
		return func
	  return decorator
 
    def post(self, path: str) -> Callable[[Callable[..., Any]], [Callable[..., Any]]:
        def decorator(func: [Callable[..., Any]) -> [Callable[..., Any]:
	      self.add_api_route(path, func, method=”post”)
		return func
	  return decorator