"""
Pydantic schemas for request/response validation.

Provides data models for API endpoints with validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ============== User Schemas ==============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""
    firebase_uid: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    firebase_uid: str
    created_at: datetime
    notification_enabled: bool
    
    class Config:
        from_attributes = True


# ============== Route Schemas ==============

class RouteBase(BaseModel):
    """Base route schema."""
    label: str = Field(..., min_length=1, max_length=100)
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    origin_address: Optional[str] = None
    destination_address: Optional[str] = None
    delay_threshold_minutes: int = Field(default=10, ge=1, le=120)


class RouteCreate(RouteBase):
    """Schema for creating a route."""
    active_days: Optional[List[int]] = [0, 1, 2, 3, 4]  # Mon-Fri
    active_time_start: Optional[str] = None  # "07:30"
    active_time_end: Optional[str] = None    # "09:00"


class RouteUpdate(BaseModel):
    """Schema for updating a route."""
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    delay_threshold_minutes: Optional[int] = Field(None, ge=1, le=120)
    active_days: Optional[List[int]] = None
    active_time_start: Optional[str] = None
    active_time_end: Optional[str] = None
    is_active: Optional[bool] = None


class RouteResponse(RouteBase):
    """Schema for route response."""
    id: int
    user_id: int
    active_days: List[int]
    active_time_start: Optional[str]
    active_time_end: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Traffic Check Schemas ==============

class TrafficCheckBase(BaseModel):
    """Base traffic check schema."""
    duration_normal: Optional[int] = None
    duration_in_traffic: Optional[int] = None
    delay_minutes: Optional[float] = None
    incident_data: Optional[dict] = None
    alternate_duration: Optional[int] = None
    alternate_route_summary: Optional[str] = None
    ai_alert_message: Optional[str] = None
    alert_sent: bool = False


class TrafficCheckCreate(TrafficCheckBase):
    """Schema for creating a traffic check."""
    route_id: int


class TrafficCheckResponse(TrafficCheckBase):
    """Schema for traffic check response."""
    id: int
    route_id: int
    checked_at: datetime
    
    class Config:
        from_attributes = True


# ============== Notification Schemas ==============

class NotificationBase(BaseModel):
    """Base notification schema."""
    message: str
    delivery_status: str = "sent"
    error_message: Optional[str] = None
    ai_model_used: Optional[str] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: int
    route_id: int


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: int
    user_id: int
    route_id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True


# ============== Google Maps API Schemas ==============

class GoogleMapsRouteRequest(BaseModel):
    """Schema for Google Maps Routes API request."""
    origin: dict
    destination: dict
    travel_mode: str = "DRIVE"
    routing_preference: str = "TRAFFIC_AWARE"


class GoogleMapsRouteResponse(BaseModel):
    """Schema for Google Maps Routes API response."""
    duration_seconds: int
    distance_meters: int
    duration_in_traffic_seconds: Optional[int] = None
    route_summary: str
    incidents: Optional[list] = None
