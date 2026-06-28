"""
User Service Module
Handles all user-related business logic with proper abstraction
"""

from sqlmodel import Session, select
from fastapi import HTTPException, status
from backend.app.db.models import User
from backend.app.schemas import UserCreate


class UserService:
    @staticmethod
    def create_user(session: Session, user_in: UserCreate) -> User:
        """
        Create a new user in the database
        """
        # Check if email already exists
        existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered"
            )

        # Create new user
        new_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=user_in.password,  # This should already be hashed by the caller
            is_bot=False
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by email
        """
        return session.exec(select(User).where(User.email == email)).first()

    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID
        """
        return session.get(User, user_id)