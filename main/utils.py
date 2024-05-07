from typing import Optional, Dict, Any
from .models import Profile

def get_user_info(user: Profile, token: Optional[str] = None) -> Dict[str, Any]:
    """Get user info."""
    user_info = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'token': token,
        'email': user.email,
    }
    return user_info