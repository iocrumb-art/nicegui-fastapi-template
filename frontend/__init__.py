from fastapi import FastAPI
from nicegui import ui
from backend.core.config import settings

# Import all pages from the .pages sub-package to register their routes
from .pages import home, login, items, create_user, landing, items2, items3

def init_frontend(app: FastAPI) -> None:
    """
    Initializes and mounts the NiceGUI user interface on the FastAPI app.
    """
    # The storage_secret is essential for securely managing session data.
    # It should be a long, random string in a real application.

    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

    ui.run_with(app, storage_secret=settings.SECRET_KEY)
