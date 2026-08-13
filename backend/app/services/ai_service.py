"""
Anthropic Claude AI service for generating natural-language traffic alerts.

Converts structured traffic data into human-friendly, actionable notifications.
"""
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic

from app.core.config import settings


class AIService:
    """Service for generating AI-powered traffic alerts using Claude."""
    
    SYSTEM_PROMPT = """You are a traffic alert assistant. Your job is to convert structured traffic data into concise, friendly, and actionable notifications for commuters.

Guidelines:
- Keep messages under {max_words} words
- Be specific about the road/route name
- Mention the delay time clearly
- Provide one practical suggestion (leave earlier, take alternate route, etc.)
- Use a friendly, helpful tone
- If there's an incident (accident, construction), mention it
- Avoid technical jargon"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.AI_MODEL
        self.max_words = settings.MAX_NOTIFICATION_WORDS
    
    async def generate_alert(
        self,
        traffic_data: Dict[str, Any],
        route_label: str,
        delay_minutes: float,
        incident_info: Optional[str] = None,
        historical_context: Optional[str] = None
    ) -> str:
        """
        Generate a natural-language traffic alert.
        
        Args:
            traffic_data: Raw traffic data from Google Maps API
            route_label: User's label for the route (e.g., "Home to Work")
            delay_minutes: Current delay in minutes
            incident_info: Optional incident information
            historical_context: Optional historical pattern info
            
        Returns:
            Generated alert message string
        """
        # Build the user message with structured data
        user_message = self._build_prompt(
            traffic_data=traffic_data,
            route_label=route_label,
            delay_minutes=delay_minutes,
            incident_info=incident_info,
            historical_context=historical_context
        )
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=100,  # Keep response short
                system=self.SYSTEM_PROMPT.format(max_words=self.max_words),
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract the generated text
            alert_message = response.content[0].text.strip()
            return alert_message
            
        except Exception as e:
            # Fallback to a template message if AI fails
            return self._fallback_alert(route_label, delay_minutes, incident_info)
    
    def _build_prompt(
        self,
        traffic_data: Dict[str, Any],
        route_label: str,
        delay_minutes: float,
        incident_info: Optional[str],
        historical_context: Optional[str]
    ) -> str:
        """Build the prompt for the AI model."""
        
        prompt_parts = [
            f"Route: {route_label}",
            f"Current delay: {delay_minutes:.1f} minutes",
            f"Normal duration: {traffic_data.get('duration_seconds', 0) / 60:.1f} minutes",
            f"With traffic: {traffic_data.get('duration_in_traffic_seconds', 0) / 60:.1f} minutes",
            f"Distance: {traffic_data.get('distance_meters', 0) / 1000:.1f} km",
        ]
        
        if traffic_data.get('route_summary'):
            prompt_parts.append(f"Route description: {traffic_data['route_summary']}")
        
        if incident_info:
            prompt_parts.append(f"Incident: {incident_info}")
        
        if historical_context:
            prompt_parts.append(f"Historical pattern: {historical_context}")
        
        if traffic_data.get('alternatives'):
            alt_info = []
            for i, alt in enumerate(traffic_data['alternatives'][:2], 1):
                alt_duration = alt.get('duration_seconds', 0) / 60
                alt_summary = alt.get('summary', 'Alternative')
                alt_info.append(f"Alt {i}: {alt_summary} ({alt_duration:.1f} min)")
            if alt_info:
                prompt_parts.append("Alternatives: " + "; ".join(alt_info))
        
        prompt_parts.append("\nGenerate a concise, actionable traffic alert (under {max_words} words).")
        
        return "\n".join(prompt_parts)
    
    def _fallback_alert(
        self,
        route_label: str,
        delay_minutes: float,
        incident_info: Optional[str] = None
    ) -> str:
        """Generate a fallback alert if AI service fails."""
        
        base_msg = f"Traffic on {route_label}: {delay_minutes:.0f}-min delay expected."
        
        if incident_info:
            return f"{base_msg} Due to {incident_info.lower()}. Consider leaving earlier."
        
        if delay_minutes > 20:
            return f"{base_msg} Heavy congestion. Leave {int(delay_minutes/2)} min earlier to avoid it."
        elif delay_minutes > 10:
            return f"{base_msg} Moderate delays. Check alternate routes."
        else:
            return f"{base_msg} Minor slowdowns."
    
    async def analyze_patterns(
        self,
        traffic_history: list
    ) -> str:
        """
        Analyze historical traffic patterns to identify recurring issues.
        
        Args:
            traffic_history: List of past traffic check records
            
        Returns:
            Summary of identified patterns
        """
        if not traffic_history:
            return "Insufficient data for pattern analysis."
        
        # Prepare summary statistics
        avg_delay = sum(record.get('delay_minutes', 0) for record in traffic_history) / len(traffic_history)
        max_delay = max(record.get('delay_minutes', 0) for record in traffic_history)
        high_delay_count = sum(1 for record in traffic_history if record.get('delay_minutes', 0) > 15)
        
        prompt = f"""Analyze this traffic history and identify recurring patterns in 1-2 sentences:

- Total checks: {len(traffic_history)}
- Average delay: {avg_delay:.1f} minutes
- Maximum delay: {max_delay:.1f} minutes
- High delay occurrences (>15 min): {high_delay_count}

Recent checks:
{chr(10).join(f"- {record.get('checked_at', 'Unknown')}: {record.get('delay_minutes', 0):.1f} min delay" for record in traffic_history[-5:])}

Summarize any recurring congestion patterns."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=150,
                system="You are a traffic pattern analyst. Summarize recurring congestion patterns concisely.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception:
            return f"This route averages {avg_delay:.1f} min delay. {high_delay_count} significant delays recorded."


# Singleton instance
ai_service = AIService()
