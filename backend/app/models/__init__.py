"""
Database models for RoadPulse.

Defines SQLAlchemy ORM models for users, saved routes, traffic checks, and notifications.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, JSON, Text, ARRAY
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """User model for authentication and preferences."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    firebase_uid = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notification_enabled = Column(Boolean, default=True)
    
    # Relationships
    saved_routes = relationship("SavedRoute", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class SavedRoute(Base):
    """Saved route that user wants to monitor."""
    
    __tablename__ = "saved_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(100), nullable=False)  # e.g., "Home to Work"
    
    # Origin coordinates
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    origin_address = Column(String(500))
    
    # Destination coordinates
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    destination_address = Column(String(500))
    
    # Active schedule (for commute windows)
    active_days = Column(JSON, default=[0, 1, 2, 3, 4])  # Mon-Fri (0=Monday)
    active_time_start = Column(String(8))  # "07:30"
    active_time_end = Column(String(8))    # "09:00"
    
    # Alert threshold
    delay_threshold_minutes = Column(Integer, default=10)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_routes")
    traffic_checks = relationship("TrafficCheck", back_populates="route", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="route", cascade="all, delete-orphan")


class TrafficCheck(Base):
    """Historical traffic check data for analysis."""
    
    __tablename__ = "traffic_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("saved_routes.id"), nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Traffic data from Google Maps Routes API
    duration_normal = Column(Integer)  # Duration in seconds without traffic
    duration_in_traffic = Column(Integer)  # Duration in seconds with current traffic
    delay_minutes = Column(Float)  # Calculated delay
    
    # Optional incident data
    incident_data = Column(JSON)  # Any incidents along the route
    
    # Alternate route comparison (optional)
    alternate_duration = Column(Integer)
    alternate_route_summary = Column(String(500))
    
    # AI-generated alert (if triggered)
    ai_alert_message = Column(Text)
    alert_sent = Column(Boolean, default=False)
    
    # Relationships
    route = relationship("SavedRoute", back_populates="traffic_checks")


class Notification(Base):
    """Record of notifications sent to users."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("saved_routes.id"), nullable=False)
    
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Delivery status
    delivery_status = Column(String(50), default="sent")  # sent, failed, delivered
    error_message = Column(Text)
    
    # AI metadata
    ai_model_used = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    route = relationship("SavedRoute", back_populates="notifications")
