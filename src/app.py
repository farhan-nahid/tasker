from .factory import create_app
from .modules import health_router


# Create the application instance using the factory
app = create_app()


# Register module routers
app.include_router(health_router)