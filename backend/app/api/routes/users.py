"""
User management API routes.

Handles user registration, profile retrieval, and preferences.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import User, SavedRoute, Notification
from app.schemas import UserCreate, UserResponse, RouteResponse, NotificationResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    This is typically called after Firebase authentication succeeds.
    The frontend should send the Firebase UID along with email.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.firebase_uid == user_data.firebase_uid)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or Firebase UID already exists"
        )
    
    # Create new user
    db_user = User(
        email=user_data.email,
        firebase_uid=user_data.firebase_uid,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/me", response_model=UserResponse)
def get_current_user(
    firebase_uid: str,  # In production, extract from Firebase token
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    
    In production, firebase_uid should be extracted from validated Firebase JWT token.
    """
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/me/routes", response_model=List[RouteResponse])
def get_user_routes(
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get all saved routes for the current user.
    """
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user.saved_routes


@router.get("/me/notifications", response_model=List[NotificationResponse])
def get_user_notifications(
    firebase_uid: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent notifications for the current user.
    """
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    notifications = db.query(Notification).filter(
        Notification.user_id == user.id
    ).order_by(Notification.sent_at.desc()).limit(limit).all()
    
    return notifications
