"""
API Response Formatting

Provides consistent response formatting for all API endpoints.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import Response as FlaskResponse
from flask import jsonify


class APIResponse:
    """Utility class for formatting API responses."""
    
    @staticmethod
    def success(data: Any, message: Optional[str] = None, status_code: int = 200) -> FlaskResponse:
        """
        Create a successful API response.
        
        Args:
            data: Response data (dict, list, or primitive)
            message: Optional success message
            status_code: HTTP status code (default: 200)
        
        Returns:
            Flask Response object with JSON content.
        """
        response_data = {
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        if message:
            response_data["message"] = message
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def error(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> FlaskResponse:
        """
        Create an error API response.
        
        Args:
            message: Error message
            status_code: HTTP status code (default: 400)
            details: Optional error details
        
        Returns:
            Flask Response object with JSON content.
        """
        response_data = {
            "success": False,
            "error": {
                "message": message,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
        
        if details:
            response_data["error"]["details"] = details
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def health_response(status: str, components: Dict[str, str], metrics: Dict[str, Any]) -> FlaskResponse:
        """
        Create a standardized health check response.
        
        Args:
            status: Overall status ("healthy", "unhealthy", "degraded")
            components: Component health statuses
            metrics: System metrics
        
        Returns:
            Flask Response object with health check JSON.
        """
        response_data = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "components": components,
            "metrics": metrics
        }
        
        # Set appropriate status code
        if status == "healthy":
            status_code = 200
        elif status == "degraded":
            status_code = 200  # Still operational
        else:
            status_code = 503
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def json_response(data: Any, status_code: int = 200, content_type: str = "application/json") -> FlaskResponse:
        """
        Create a raw JSON response.
        
        Args:
            data: Response data
            status_code: HTTP status code
            content_type: Content-Type header
        
        Returns:
            Flask Response object.
        """
        response = FlaskResponse(
            json.dumps(data, indent=2),
            status=status_code,
            content_type=content_type
        )
        return response


class HealthResponseFormatter:
    """Formatter specifically for health check responses."""
    
    @staticmethod
    def format(
        status: str,
        components: Dict[str, str],
        metrics: Dict[str, Any],
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format a health check response.
        
        Args:
            status: Overall status ("healthy", "unhealthy", "degraded")
            components: Component health statuses
            metrics: System metrics
            version: Optional version string
        
        Returns:
            Formatted health check dictionary.
        """
        response = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "components": components,
            "metrics": metrics
        }
        
        if version:
            response["version"] = version
        
        return response
    
    @staticmethod
    def to_json(
        status: str,
        components: Dict[str, str],
        metrics: Dict[str, Any],
        version: Optional[str] = None,
        indent: int = 2
    ) -> str:
        """
        Format health check as JSON string.
        
        Args:
            status: Overall status
            components: Component health statuses
            metrics: System metrics
            version: Optional version string
            indent: JSON indentation level
        
        Returns:
            Formatted JSON string.
        """
        response = HealthResponseFormatter.format(status, components, metrics, version)
        return json.dumps(response, indent=indent)
