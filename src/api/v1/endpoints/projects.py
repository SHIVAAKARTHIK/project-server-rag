from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.schemas.project import (
    ProjectCreate,
    ProjectSettingsUpdate,
)
from src.services.database.repositories.project_repo import (
    ProjectRepository,
    ProjectSettingsRepository,
)

router = APIRouter()

project_repo = ProjectRepository()
settings_repo = ProjectSettingsRepository()


@router.get("")
async def get_projects(clerk_id: CurrentUser):
    """Get all projects for the current user."""
    projects = project_repo.get_all(clerk_id=clerk_id)
    
    return {
        "message": "Projects retrieved successfully",
        "data": projects
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, clerk_id: CurrentUser):
    """Create a new project with default settings."""
    try:
        # Create project
        project = project_repo.create({
            "name": project_data.name,
            "description": project_data.description,
            "clerk_id": clerk_id
        })
        
        # Create default settings
        try:
            settings_repo.create_default(project["id"])
        except Exception as e:
            # Rollback project creation
            project_repo.delete(project["id"])
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to create project settings - project creation rolled back"
            )
        
        return {
            "message": "Project created successfully",
            "data": project
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/{project_id}")
async def get_project(project_id: str, clerk_id: CurrentUser):
    """Get a specific project by ID."""
    project = project_repo.get_by_id(project_id, clerk_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "message": "Project retrieved successfully",
        "data": project
    }


@router.delete("/{project_id}")
async def delete_project(project_id: str, clerk_id: CurrentUser):
    """Delete a project (CASCADE deletes related data)."""
    # Verify ownership
    if not project_repo.exists(project_id, clerk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    deleted = project_repo.delete(project_id, clerk_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
    
    return {
        "message": "Project deleted successfully",
        "data": deleted
    }


@router.get("/{project_id}/settings")
async def get_project_settings(project_id: str, clerk_id: CurrentUser):
    """Get project settings."""
    # Verify project access
    if not project_repo.exists(project_id, clerk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    settings = settings_repo.get_by_project_id(project_id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project settings not found"
        )
    
    return {
        "message": "Project settings retrieved successfully",
        "data": settings
    }


@router.put("/{project_id}/settings")
async def update_project_settings(
    project_id: str,
    settings_data: ProjectSettingsUpdate,
    clerk_id: CurrentUser
):
    """Update project settings."""
    # Verify project access
    if not project_repo.exists(project_id, clerk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Filter out None values
    update_data = {k: v for k, v in settings_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    updated = settings_repo.update_by_project_id(project_id, update_data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project settings not found"
        )
    
    return {
        "message": "Project settings updated successfully",
        "data": updated
    }


@router.get("/{project_id}/chats")
async def get_project_chats(project_id: str, clerk_id: CurrentUser):
    """Get all chats for a project."""
    from src.services.database.repositories.chat_repo import ChatRepository
    
    chat_repo = ChatRepository()
    chats = chat_repo.get_by_project(project_id, clerk_id)
    
    return {
        "message": "Project chats retrieved successfully",
        "data": chats
    }
