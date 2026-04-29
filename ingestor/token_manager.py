import json
import os

# Canonical token location — managed by tfresh2 (token refresher cron)
DEFAULT_TOKEN_PATH = os.path.expanduser("~/projects/tfresh2/token.json")


class TokenManager:
    """Manages access tokens for TradeStation API."""

    def __init__(self, token_path: str = DEFAULT_TOKEN_PATH):
        self.token_path = token_path

    def get_access_token(self) -> str | None:
        """Reads the access token from the specified JSON file."""
        try:
            with open(self.token_path, "r") as f:
                data = json.load(f)
                return data.get("access_token")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading token file ({self.token_path}): {e}")
            return None

    def get_token_expiry(self) -> float | None:
        """Returns the token expiry timestamp, or None if not available."""
        try:
            with open(self.token_path, "r") as f:
                data = json.load(f)
                return data.get("expires_at")
        except (FileNotFoundError, json.JSONDecodeError):
            return None
