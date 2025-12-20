from fastapi import APIRouter

from src.api.v1.endpoints import projects, files, chats, messages,webhooks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)

api_router.include_router(
    files.router,
    prefix="/projects",
    tags=["Files"]
)

api_router.include_router(
    chats.router,
    prefix="/chats",
    tags=["Chats"]
)

api_router.include_router(
    messages.router,
    prefix="/projects",
    tags=["Messages"]
)

api_router.include_router(
    webhooks.router,
    prefix="/webhook",
    tags=["Webhooks"]
)
