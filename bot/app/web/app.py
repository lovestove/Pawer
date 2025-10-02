import aiohttp_cors
from pathlib import Path
from aiohttp import web

from .routes import get_pet_data, interact_with_pet

# Define the path to the static files directory at the module level
static_files_path = Path(__file__).parent.parent.parent.joinpath("mini_app")


async def index(request: web.Request) -> web.FileResponse:
    """
    Serves the main index.html file for the Mini App.
    """
    return web.FileResponse(static_files_path / "index.html")


def setup_routes(app: web.Application):
    """Set up the application's routes."""
    # API routes
    app.router.add_get("/api/pet", get_pet_data)
    app.router.add_post("/api/pet/interact", interact_with_pet)

    # Static files route
    app.router.add_static("/static/", path=static_files_path, name="static")

    # Main route for the Mini App's entry point
    app.router.add_get("/", index)


def setup_cors(app: web.Application):
    """Set up CORS for the application."""
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        },
    )
    for route in list(app.router.routes()):
        cors.add(route)


def create_web_app(db):
    """Create and configure the web application."""
    app = web.Application()
    app["db"] = db
    setup_routes(app)
    setup_cors(app)
    return app