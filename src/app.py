from .configs.database import Base, engine
from .core import create_app
from .modules import health_router


# Create the application instance using the factory
app = create_app()

""" 
Only uncomment below to create new tables, 
otherwise the tests will fail if not connected
"""
Base.metadata.create_all(bind=engine)

# Register module routers
app.include_router(health_router)