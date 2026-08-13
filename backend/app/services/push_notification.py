"""
Firebase Cloud Messaging service for push notifications.

Handles sending push notifications to iOS and Android devices.
"""
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, messaging
from datetime import datetime

from app.core.config import settings


class PushNotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging."""
    
    def __init__(self):
        self.initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.FIREBASE_PROJECT_ID
            })
            self.initialized = True
        except FileNotFoundError:
            print(f"Warning: Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}")
            print("Push notifications will not work until credentials are provided.")
            self.initialized = False
        except Exception as e:
            print(f"Warning: Failed to initialize Firebase: {e}")
            self.initialized = False
    
    async def send_traffic_alert(
        self,
        device_tokens: List[str],
        route_label: str,
        message: str,
        delay_minutes: float
    ) -> dict:
        """
        Send a traffic alert push notification.
        
        Args:
            device_tokens: List of FCM device tokens
            route_label: User's label for the route
            message: AI-generated alert message
            delay_minutes: Current delay in minutes
            
        Returns:
            Response summary from FCM
        """
        if not self.initialized:
            return {"success": False, "error": "Firebase not initialized"}
        
        if not device_tokens:
            return {"success": False, "error": "No device tokens provided"}
        
        # Build notification payload
        notification = messaging.Notification(
            title=f"Traffic Alert: {route_label}",
            body=message,
        )
        
        # Add data payload for app handling
        data = {
            "type": "traffic_alert",
            "route_label": route_label,
            "delay_minutes": str(delay_minutes),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Send multicast message
        try:
            response = messaging.send_multicast(
                messaging.MulticastMessage(
                    notification=notification,
                    data=data,
                    tokens=device_tokens,
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            sound="default",
                            color="#FF6B6B"  # Red-orange for alerts
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound="default",
                                badge=1,
                            )
                        )
                    ),
                )
            )
            
            return {
                "success": True,
                "total_sent": response.success_count,
                "failed_count": response.failure_count,
                "responses": response.responses
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_test_notification(
        self,
        device_token: str
    ) -> dict:
        """
        Send a test notification.
        
        Args:
            device_token: Single FCM device token
            
        Returns:
            Response from FCM
        """
        if not self.initialized:
            return {"success": False, "error": "Firebase not initialized"}
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="RoadPulse Test",
                    body="Your notification system is working!",
                ),
                data={"type": "test"},
                token=device_token,
            )
            
            response = messaging.send(message)
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
push_service = PushNotificationService()
