from typing import Optional
from sqlmodel import Session, select
from backend.core.security import get_password_hash, verify_password
from backend.models.models import User, UserCreate


class UserRepository:
    def get(self, db: Session, id: int) -> Optional[Item]:
        """Retrieves a single user from the database by its primary key ID."""
        return db.get(User, id)

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Finds and returns a user by their email address."""
        return db.exec(select(User).where(User.email == email)).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        """Retrieves a list of all items, with options for pagination."""
        return db.exec(select(User).offset(skip).limit(limit)).all()


    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Creates a new user record in the database,
        hashing the provided password for storage."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Validates a user's credentials by checking their email and verifying their password."""
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def remove(self, db: Session, *, id: int) -> Item:
        """Deletes a specific user from the database by its ID."""
        obj = db.get(User, id)
        db.delete(obj)
        db.commit()
        return obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Updates the password of an existing user in the database."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository()
