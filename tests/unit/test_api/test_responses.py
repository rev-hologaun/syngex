"""
tests/unit/test_api/test_responses.py

Unit tests for API response formatters.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from api.responses import APIResponse, HealthResponseFormatter


class TestAPIResponse:
    """Tests for APIResponse class."""

    def test_success_response_basic(self):
        """Test success response with basic data."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.success({"key": "value"})

            assert status_code == 200
            mock_jsonify.assert_called_once()

    def test_success_response_with_message(self):
        """Test success response with message."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.success(
                {"key": "value"},
                message="Success!"
            )

            # Check that jsonify was called with message
            call_args = mock_jsonify.call_args[0][0]
            assert "message" in call_args
            assert call_args["message"] == "Success!"

    def test_success_response_custom_status(self):
        """Test success response with custom status code."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.success(
                {"key": "value"},
                status_code=201
            )

            assert status_code == 201

    def test_error_response_basic(self):
        """Test error response."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.error("Error message")

            assert status_code == 400
            call_args = mock_jsonify.call_args[0][0]
            assert call_args["success"] is False
            assert call_args["error"]["message"] == "Error message"

    def test_error_response_with_details(self):
        """Test error response with details."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.error(
                "Error message",
                details={"field": "value"}
            )

            call_args = mock_jsonify.call_args[0][0]
            assert call_args["error"]["details"] == {"field": "value"}

    def test_error_response_custom_status(self):
        """Test error response with custom status code."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.error(
                "Not found",
                status_code=404
            )

            assert status_code == 404

    def test_health_response_healthy(self):
        """Test health response for healthy status."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.health_response(
                status="healthy",
                components={"calc": "healthy"},
                metrics={"uptime": 3600}
            )

            assert status_code == 200

    def test_health_response_degraded(self):
        """Test health response for degraded status."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.health_response(
                status="degraded",
                components={"calc": "healthy"},
                metrics={}
            )

            assert status_code == 200

    def test_health_response_unhealthy(self):
        """Test health response for unhealthy status."""
        with patch('api.responses.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            response, status_code = APIResponse.health_response(
                status="unhealthy",
                components={"calc": "unhealthy"},
                metrics={}
            )

            assert status_code == 503

    def test_json_response(self):
        """Test raw JSON response."""
        response = APIResponse.json_response({"key": "value"}, status_code=200)

        assert response is not None


class TestHealthResponseFormatter:
    """Tests for HealthResponseFormatter class."""

    def test_format_basic(self):
        """Test format() with basic inputs."""
        result = HealthResponseFormatter.format(
            status="healthy",
            components={"calc": "healthy"},
            metrics={"uptime": 3600}
        )

        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert result["components"]["calc"] == "healthy"
        assert result["metrics"]["uptime"] == 3600

    def test_format_with_version(self):
        """Test format() with version."""
        result = HealthResponseFormatter.format(
            status="healthy",
            components={},
            metrics={},
            version="1.0.0"
        )

        assert result["version"] == "1.0.0"

    def test_to_json(self):
        """Test to_json() produces valid JSON string."""
        result = HealthResponseFormatter.to_json(
            status="healthy",
            components={"calc": "healthy"},
            metrics={}
        )

        assert isinstance(result, str)
        assert "healthy" in result
        assert "timestamp" in result

    def test_to_json_with_indent(self):
        """Test to_json() with custom indent."""
        result = HealthResponseFormatter.to_json(
            status="healthy",
            components={},
            metrics={},
            indent=4
        )

        # Should have 4-space indentation
        assert "    " in result  # 4 spaces
