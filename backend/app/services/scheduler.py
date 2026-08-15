"""
Background scheduler for traffic monitoring.

Polls saved routes at configured intervals and triggers alerts when delays exceed thresholds.
"""
from datetime import datetime, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import asyncio

from app.db.session import SessionLocal
from app.models import SavedRoute, TrafficCheck, Notification, User
from app.services.google_maps import google_maps_service
from app.services.ai_service import ai_service
from app.services.push_notification import push_service
from app.core.config import settings


class TrafficMonitorScheduler:
    """Scheduler that periodically checks traffic on saved routes."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            return
        
        # Add job to poll routes every N minutes
        self.scheduler.add_job(
            self._check_all_routes,
            trigger=CronTrigger(minute=f"*/{settings.POLL_INTERVAL_MINUTES}"),
            id="traffic_poll",
            name="Poll all active routes",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        print(f"Traffic monitor started (polling every {settings.POLL_INTERVAL_MINUTES} minutes)")
    
    def stop(self):
        """Stop the background scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            print("Traffic monitor stopped")
    
    async def _check_all_routes(self):
        """Check traffic conditions for all active routes."""
        db = SessionLocal()
        try:
            # Get all active routes
            routes = db.query(SavedRoute).filter(
                SavedRoute.is_active == True
            ).all()
            
            now = datetime.utcnow()
            current_time = now.time()
            current_weekday = now.weekday()  # 0 = Monday
            
            for route in routes:
                # Check if within active time window
                if not self._is_within_active_window(
                    route, current_time, current_weekday
                ):
                    continue
                
                # Check traffic for this route
                await self._check_route_traffic(db, route)
                
        except Exception as e:
            print(f"Error checking routes: {e}")
        finally:
            db.close()
    
    def _is_within_active_window(
        self,
        route: SavedRoute,
        current_time: time,
        current_weekday: int
    ) -> bool:
        """Check if current time is within route's active window."""
        
        # Check if today is an active day
        if route.active_days and current_weekday not in route.active_days:
            return False
        
        # Check if within time window (if specified)
        if route.active_time_start and route.active_time_end:
            try:
                start_time = datetime.strptime(route.active_time_start, "%H:%M").time()
                end_time = datetime.strptime(route.active_time_end, "%H:%M").time()
                
                if start_time <= end_time:
                    # Normal case: e.g., 07:30 - 09:00
                    if not (start_time <= current_time <= end_time):
                        return False
                else:
                    # Overnight case: e.g., 22:00 - 06:00
                    if not (current_time >= start_time or current_time <= end_time):
                        return False
            except ValueError:
                pass  # Invalid time format, skip time check
        
        return True
    
    async def _check_route_traffic(self, db: Session, route: SavedRoute):
        """Check traffic for a specific route and send alert if needed."""
        
        # Get current traffic data from Google Maps
        traffic_data = await google_maps_service.get_route_traffic(
            origin_lat=route.origin_lat,
            origin_lng=route.origin_lng,
            destination_lat=route.destination_lat,
            destination_lng=route.destination_lng
        )
        
        if "error" in traffic_data:
            print(f"Error getting traffic for route {route.id}: {traffic_data['error']}")
            return
        
        # Calculate delay
        duration_normal = traffic_data.get("duration_seconds", 0)
        duration_in_traffic = traffic_data.get("duration_in_traffic_seconds", duration_normal)
        delay_minutes = (duration_in_traffic - duration_normal) / 60
        
        # Check if delay exceeds threshold
        if delay_minutes < route.delay_threshold_minutes:
            # No alert needed, but still log the check
            self._log_traffic_check(db, route, traffic_data, delay_minutes)
            return
        
        # Generate AI alert message
        alert_message = await ai_service.generate_alert(
            traffic_data=traffic_data,
            route_label=route.label,
            delay_minutes=delay_minutes
        )
        
        # Log the traffic check with alert
        traffic_check = self._log_traffic_check(
            db, route, traffic_data, delay_minutes,
            ai_alert_message=alert_message
        )
        
        # Get user's device tokens and send notification
        user = db.query(User).filter(User.id == route.user_id).first()
        if user and user.notification_enabled:
            # In production, get device tokens from a DeviceToken table
            # For now, this is a placeholder
            device_tokens = []  # TODO: Fetch from database
            
            if device_tokens:
                notification_result = await push_service.send_traffic_alert(
                    device_tokens=device_tokens,
                    route_label=route.label,
                    message=alert_message,
                    delay_minutes=delay_minutes
                )
                
                # Log notification
                self._log_notification(
                    db, user, route, alert_message,
                    notification_result, traffic_check
                )
    
    def _log_traffic_check(
        self,
        db: Session,
        route: SavedRoute,
        traffic_data: dict,
        delay_minutes: float,
        ai_alert_message: Optional[str] = None
    ) -> TrafficCheck:
        """Log a traffic check to the database."""
        
        check = TrafficCheck(
            route_id=route.id,
            duration_normal=traffic_data.get("duration_seconds"),
            duration_in_traffic=traffic_data.get("duration_in_traffic_seconds"),
            delay_minutes=delay_minutes,
            incident_data=traffic_data.get("incidents"),
            alternate_duration=(
                traffic_data["alternatives"][0]["duration_seconds"]
                if traffic_data.get("alternatives") else None
            ),
            ai_alert_message=ai_alert_message,
            alert_sent=(ai_alert_message is not None)
        )
        
        db.add(check)
        db.commit()
        db.refresh(check)
        
        return check
    
    def _log_notification(
        self,
        db: Session,
        user: User,
        route: SavedRoute,
        message: str,
        notification_result: dict,
        traffic_check: TrafficCheck
    ):
        """Log a sent notification to the database."""
        
        from app.core.config import settings
        
        notification = Notification(
            user_id=user.id,
            route_id=route.id,
            message=message,
            delivery_status=(
                "sent" if notification_result.get("success") else "failed"
            ),
            error_message=notification_result.get("error"),
            ai_model_used=settings.AI_MODEL
        )
        
        db.add(notification)
        db.commit()


# Singleton instance
scheduler = TrafficMonitorScheduler()


def start_scheduler():
    """Start the traffic monitoring scheduler."""
    scheduler.start()


def stop_scheduler():
    """Stop the traffic monitoring scheduler."""
    scheduler.stop()
