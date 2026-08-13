"""
Route management API routes.

Handles CRUD operations for saved routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import User, SavedRoute, TrafficCheck
from app.schemas import RouteCreate, RouteResponse, RouteUpdate, TrafficCheckResponse

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


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    route_data: RouteCreate,
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Create a new saved route for the current user.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    # Create new route
    db_route = SavedRoute(
        user_id=user.id,
        **route_data.model_dump(),
    )
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    
    return db_route


@router.get("/", response_model=List[RouteResponse])
def get_user_routes(
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get all saved routes for the current user.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    routes = db.query(SavedRoute).filter(
        SavedRoute.user_id == user.id,
        SavedRoute.is_active == True
    ).all()
    
    return routes


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(
    route_id: int,
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific route by ID.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    route = db.query(SavedRoute).filter(
        SavedRoute.id == route_id,
        SavedRoute.user_id == user.id
    ).first()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    return route


@router.patch("/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int,
    route_data: RouteUpdate,
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Update a route's settings.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    route = db.query(SavedRoute).filter(
        SavedRoute.id == route_id,
        SavedRoute.user_id == user.id
    ).first()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    # Update only provided fields
    update_data = route_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(route, field, value)
    
    db.commit()
    db.refresh(route)
    
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a saved route.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    route = db.query(SavedRoute).filter(
        SavedRoute.id == route_id,
        SavedRoute.user_id == user.id
    ).first()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    db.delete(route)
    db.commit()
    
    return None


@router.get("/{route_id}/traffic-history", response_model=List[TrafficCheckResponse])
def get_route_traffic_history(
    route_id: int,
    firebase_uid: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get traffic check history for a specific route.
    """
    user = get_user_by_firebase_uid(db, firebase_uid)
    
    route = db.query(SavedRoute).filter(
        SavedRoute.id == route_id,
        SavedRoute.user_id == user.id
    ).first()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    checks = db.query(TrafficCheck).filter(
        TrafficCheck.route_id == route.id
    ).order_by(TrafficCheck.checked_at.desc()).limit(limit).all()
    
    return checks
