from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend import models
from backend.api import deps
from backend.repositories.user import user_repo

router = APIRouter()


@router.post("/user/", response_model=models.UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: models.UserCreate,
    _current_user: models.User = Depends(
        deps.get_current_active_superuser
    ),  # 403 if not superuser
) -> Any:
    """Creates a new user, a function restricted to superusers,
    and prevents the creation of users with duplicate email addresses."""
    user = user_repo.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_repo.create(db, obj_in=user_in)
    return user

@router.get("/userlist/", response_model=List[models.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Retrieves a list of items, either all items for a superuser or
    only the items belonging to the current user."""
    if current_user.is_superuser:
        users = user_repo.get_multi(db)
    else:
        users = user_repo.get_multi(db)
    return users 


@router.delete("/user/{user_id}", response_model=models.UserRead)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a user.
    """
    user = user_repo.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser and (user.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = user_repo.remove(db=db, id=user_id)
    return user

#################################################################
###  USER PW modify

@router.put("/user/{user_id}", response_model=models.UserRead)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: models.User,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a User
    """
    user = user_repo.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = user_repo.update(db=db, db_obj=user, obj_in=user_in)
    return user
