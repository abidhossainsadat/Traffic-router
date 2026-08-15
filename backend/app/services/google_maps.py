"""
Google Maps Platform integration service.

Handles communication with Google Maps Routes API for traffic-aware routing data.
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings


class GoogleMapsService:
    """Service for interacting with Google Maps Platform APIs."""
    
    BASE_URL = "https://routes.googleapis.com/directions/v2"
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.localizedValues"
        }
    
    async def get_route_traffic(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get route information with current traffic conditions.
        
        Args:
            origin_lat: Origin latitude
            origin_lng: Origin longitude
            destination_lat: Destination latitude
            destination_lng: Destination longitude
            departure_time: Departure time (defaults to now)
            
        Returns:
            Dictionary containing route duration, distance, and traffic data
        """
        url = f"{self.BASE_URL}:computeRoutes"
        
        # Build request payload
        payload = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin_lat,
                        "longitude": origin_lng
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination_lat,
                        "longitude": destination_lng
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": True,
            "languageCode": "en-US",
        }
        
        # Add departure time if specified
        if departure_time:
            payload["departureTime"] = departure_time.isoformat() + "Z"
        else:
            payload["departureTime"] = "NOW"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Parse response
                if not data.get("routes"):
                    return {"error": "No routes found"}
                
                primary_route = data["routes"][0]
                
                # Extract duration in seconds
                duration_str = primary_route.get("duration", "0s")
                duration_seconds = self._parse_duration(duration_str)
                
                # Extract localized values for traffic-aware duration
                localized_values = primary_route.get("localizedValues", {})
                traffic_duration_str = localized_values.get("duration", {}).get("text", "")
                
                # Try to get durationInTraffic from the response
                duration_in_traffic = None
                if "trafficSpeeds" in primary_route or "durationInTraffic" in primary_route:
                    traffic_duration_str = primary_route.get("durationInTraffic", duration_str)
                    duration_in_traffic = self._parse_duration(traffic_duration_str)
                
                # Get distance
                distance_meters = primary_route.get("distanceMeters", 0)
                
                # Get route summary
                route_summary = primary_route.get("description", "Route")
                
                # Get alternative routes if available
                alternatives = []
                for alt_route in data.get("routes", [])[1:3]:  # Get up to 2 alternatives
                    alt_duration = self._parse_duration(alt_route.get("duration", "0s"))
                    alt_summary = alt_route.get("description", "Alternative route")
                    alternatives.append({
                        "duration_seconds": alt_duration,
                        "summary": alt_summary
                    })
                
                return {
                    "duration_seconds": duration_seconds,
                    "duration_in_traffic_seconds": duration_in_traffic or duration_seconds,
                    "distance_meters": distance_meters,
                    "route_summary": route_summary,
                    "alternatives": alternatives,
                    "raw_response": data
                }
                
        except httpx.HTTPError as e:
            return {
                "error": f"Google Maps API error: {str(e)}",
                "status_code": getattr(e, "status_code", None)
            }
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration string to seconds.
        
        Examples:
            "120s" -> 120
            "PT2M30S" -> 150
        """
        if duration_str.endswith("s"):
            return int(duration_str[:-1])
        
        # Handle ISO 8601 format (PT1H30M)
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        
        return 0


# Singleton instance
google_maps_service = GoogleMapsService()
