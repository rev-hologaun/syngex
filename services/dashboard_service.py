"""Dashboard service - manages Streamlit subprocess."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any


class DashboardService:
    """Manages the Streamlit Command Center subprocess."""

    def __init__(
        self,
        symbol: str,
        port: int,
        data_dir: Path,
        orchestrator_ref: Any,
    ) -> None:
        self.symbol = symbol
        self._port = port
        self._data_dir = data_dir
        self._orchestrator_ref = orchestrator_ref
        self._process: subprocess.Popen | None = None
        self._logger = orchestrator_ref._logger if hasattr(orchestrator_ref, '_logger') else logging.getLogger(__name__)
        self._correlation_id = getattr(orchestrator_ref, '_correlation_id', 'unknown')

    def start(self) -> None:
        """Spawn the Streamlit Command Center as a background subprocess."""
        if self._process is not None:
            return  # already running

        # Pass symbol via environment variable so multi-instance works
        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol

        script_path = Path(__file__).parent.parent / "app_dashboard.py"
        venv_streamlit = Path(__file__).parent.parent / "venv" / "bin" / "streamlit"

        from config.logging_config import log_with_correlation

        log_with_correlation(
            self._logger, logging.INFO,
            "Starting Command Center",
            correlation_id=self._correlation_id,
            port=self._port
        )

        try:
            self._process = subprocess.Popen(
                [
                    str(venv_streamlit),
                    "run",
                    str(script_path),
                    "--server.headless",
                    "true",
                    "--browser.gatherUsageStats",
                    "false",
                    "--server.port",
                    str(self._port),
                ],
                cwd=str(Path(__file__).parent.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            log_with_correlation(
                self._logger, logging.INFO,
                "Command Center started",
                correlation_id=self._correlation_id,
                pid=self._process.pid,
                port=self._port
            )
        except FileNotFoundError:
            log_with_correlation(
                self._logger, logging.WARNING,
                "Streamlit not found, Command Center will not start",
                correlation_id=self._correlation_id,
                path=str(venv_streamlit)
            )
        except Exception as exc:
            log_with_correlation(
                self._logger, logging.WARNING,
                "Failed to start Command Center",
                correlation_id=self._correlation_id,
                error=str(exc)
            )

    def stop(self) -> None:
        """Terminate the Streamlit Command Center subprocess."""
        if self._process is None:
            return

        from config.logging_config import log_with_correlation

        log_with_correlation(
            self._logger, logging.INFO,
            "Stopping Command Center",
            correlation_id=self._correlation_id,
            pid=self._process.pid
        )
        try:
            self._process.terminate()
            self._process.wait(timeout=5)
        except Exception:
            try:
                self._process.kill()
            except Exception:
                pass
        finally:
            self._process = None

    def is_running(self) -> bool:
        """Check if the dashboard subprocess is running."""
        if self._process is None:
            return False
        return self._process.poll() is None
