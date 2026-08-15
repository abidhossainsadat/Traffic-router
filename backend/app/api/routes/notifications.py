"""
Notification API routes.

Handles notification retrieval and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import User, Notification
from app.schemas import NotificationResponse

router = APIRouter()


def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> User:
    """Helper to get user by Firebase UID."""
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    firebase_uid: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent notifications for the current user.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    notifications = db.query(Notification).filter(
        Notification.user_id == user.id
    ).order_by(Notification.sent_at.desc()).limit(limit).all()
    
    return notifications


@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get unread notifications (notifications sent in last 24 hours).
    
    Note: This is a simplified implementation. In production, you might
    want to track read/unread status explicitly.
    """
    from datetime import datetime, timedelta
    
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    # Consider notifications from last 24 hours as "unread"
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    notifications = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.sent_at >= cutoff_time
    ).order_by(Notification.sent_at.desc()).all()
    
    return notifications
