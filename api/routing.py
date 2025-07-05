from typing import Callable
from starlette.routing import Router, Any

from starlette.routing import request_response
 
def get_request_handler(
    dependant: Dependant,
) -> Callable[[Request], Coroutine[Any, Any, Response]]:
    is_coroutine = asyncio.iscoroutinefunction(dependant.call)
    async def app(request: Request) -> Response:
	  body = None
        if dependant.body_params:
            body = await request.json()
            буду
      solved_result = await solve_dependencies(
            request=request,
            dependant=dependant,
            body=body
            )
        values, errors = solved_result
        if errors: raise ValidationError(errors, RequestErrorModel)

        raw_response = await run_endpoint_function(
                dependant=dependant, values=values, is_coroutine=is_coroutine
            )
        if isinstance(raw_response, Response): return raw_response
	  if isinstance(raw_response, (dict, str, int, float, type(None))):
            return JSONResponse(raw_response)
        else: raise Exception("Type of response is not supported yet.")

    return app

class ApiRoute(routing.Router):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        method: str
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.method = method
        assert callable(endpoint), "An endpoint must be a callable"
        self.dependant = get_dependant(path=self.path, call=self.endpoint)
        self.app = request_response(get_request_handler(dependant=self.dependant))
 
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

