from typing import Annotated
from fastapi import Depends

from src.core.security import get_current_user

# Type alias for dependency injection
CurrentUser = Annotated[str, Depends(get_current_user)]
