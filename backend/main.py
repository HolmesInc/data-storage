import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from api.router import api_router
from logger import logger
from settings import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    API_DOCS_URL,
    API_REDOC_URL,
    API_OPENAPI_URL,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    UPLOADS_DIRECTORY,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    What happens:
    - Before yield: Initializes the application
    - yield: The application runs normally
    - After yield: Cleanup code would go here (if needed)

    Note: Database migrations are now handled by Alembic in the Docker entrypoint
    """

    logger.info("-" * 40)
    logger.info("Starting the server...")
    logger.info("-" * 40)

    # yield control to the application
    # The application runs while we're "inside" this context
    yield

    # SHUTDOWN: This code runs when the server shuts down
    # You can add cleanup logic here if needed
    logger.info(">> Shutting down application...")
    logger.info("-" * 40)
    logger.info(">> Cleanup completed. The server has stopped.")
    logger.info("-" * 40)


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url=API_DOCS_URL,
    redoc_url=API_REDOC_URL,
    openapi_url=API_OPENAPI_URL,
    lifespan=lifespan
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Mount static files directory for serving uploaded files
# This allows clients to download files from /uploads/ URL
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIRECTORY), name="uploads")


# Define API endpoints BEFORE mounting static files
# This ensures they take precedence over the catch-all static mount
@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Returns status to verify the API is healthy and responding.
    """
    return {"status": "healthy"}


# Include the routes from routes.py
# This makes all the endpoints defined in routes.py available
app.include_router(api_router)

# Serve static frontend files LAST
# Mount at root with html=True to serve index.html for SPA routing
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
