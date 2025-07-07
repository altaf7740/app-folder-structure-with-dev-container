from litestar import Litestar, get

@get("/")
def hello_world() -> str:
    return "Hello, World!"

app = Litestar(route_handlers=[hello_world])
