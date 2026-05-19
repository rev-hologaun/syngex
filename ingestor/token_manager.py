import json
import logging
import os
import time
from typing import Optional

# Canonical token location — managed by tfresh2 (token refresher cron)
DEFAULT_TOKEN_PATH = os.path.expanduser("~/projects/tfresh2/token.json")

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages access tokens for TradeStation API."""

    def __init__(self, token_path: str = DEFAULT_TOKEN_PATH):
        self.token_path = token_path

    def get_access_token(self) -> str | None:
        """Reads the access token from the specified JSON file."""
        try:
            with open(self.token_path, "r") as f:
                data = json.load(f)
                logger.debug(f"Successfully loaded token from {self.token_path}")
                return data.get("access_token")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading token file ({self.token_path}): {e}")
            return None

    def get_token_expiry(self) -> float | None:
        """Returns the token expiry timestamp, or None if not available."""
        try:
            with open(self.token_path, "r") as f:
                data = json.load(f)
                expiry = data.get("expires_at")
                logger.debug(f"Token expiry timestamp: {expiry}")
                return expiry
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read token expiry from {self.token_path}: {e}")
            return None

    def refresh_token_with_retry(self, max_retries: int = 3, base_delay: float = 1.0) -> Optional[str]:
        """Refreshes the token with exponential backoff retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 1.0)
            
        Returns:
            The new access token string, or None if all retries fail.
        """
        for attempt in range(max_retries):
            try:
                # Attempt to refresh token via tfresh2 cron output
                token = self.get_access_token()
                if token:
                    logger.info("Token refresh successful")
                    return token
                else:
                    logger.warning("Token refresh returned no token")
                    if attempt == max_retries - 1:
                        logger.error("Token refresh failed after all attempts - no token available")
                        return None
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Token refresh failed after {max_retries} attempts: {e}")
                    return None
                delay = base_delay * (2 ** attempt)  # exponential backoff
                logger.warning(f"Token refresh failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                time.sleep(delay)
        
        return None
