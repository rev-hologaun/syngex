"""Heatmap service - manages Flask subprocess."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any


class HeatmapService:
    """Manages the Heatmap Dashboard Flask subprocess."""

    def __init__(
        self,
        symbol: str,
        port: int,
        data_dir: Path,
        orchestrator_ref: Any,
    ) -> None:
        self.symbol = symbol
        self._base_port = port
        self._data_dir = data_dir
        self._orchestrator_ref = orchestrator_ref
        self._process: subprocess.Popen | None = None
        self._stderr_file: Any = None  # file handle for stderr
        self._logger = orchestrator_ref._logger if hasattr(orchestrator_ref, '_logger') else logging.getLogger(__name__)
        self._correlation_id = getattr(orchestrator_ref, '_correlation_id', 'unknown')

    def start(self) -> None:
        """Spawn the Heatmap Dashboard as a background subprocess on port base_port + 1."""
        if self._process is not None:
            return  # already running

        heatmap_port = self._base_port + 1

        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol
        env["HEATMAP_PORT"] = str(heatmap_port)

        script_path = Path(__file__).parent.parent / "app_heatmap.py"
        venv_python = Path(__file__).parent.parent / "venv" / "bin" / "python"
        log_path = self._data_dir.parent / "log" / "heatmap.log"

        from config.logging_config import log_with_correlation

        log_with_correlation(
            self._logger, logging.INFO,
            "Starting Heatmap Dashboard",
            correlation_id=self._correlation_id,
            port=heatmap_port
        )

        try:
            self._stderr_file = open(log_path, "a")  # append mode — avoids PIPE buffer deadlock
            self._process = subprocess.Popen(
                [
                    str(venv_python),
                    str(script_path),
                ],
                cwd=str(Path(__file__).parent.parent),
                stdout=subprocess.DEVNULL,
                stderr=self._stderr_file,
                env=env,
            )
            # Check for immediate startup failures
            ret = self._process.poll()
            if ret is not None:
                self._process.wait()
                try:
                    with open(log_path, "r") as f:
                        err_msg = f.read().strip()
                except OSError:
                    err_msg = "unknown"
                log_with_correlation(
                    self._logger, logging.WARNING,
                    "Heatmap Dashboard failed to start",
                    correlation_id=self._correlation_id,
                    exit_code=ret,
                    error=err_msg[:500]
                )
                self._process = None
                return
            log_with_correlation(
                self._logger, logging.INFO,
                "Heatmap Dashboard started",
                correlation_id=self._correlation_id,
                pid=self._process.pid,
                port=heatmap_port
            )
        except FileNotFoundError:
            log_with_correlation(
                self._logger, logging.WARNING,
                "app_heatmap.py not found, Heatmap Dashboard will not start",
                correlation_id=self._correlation_id
            )
        except Exception as exc:
            log_with_correlation(
                self._logger, logging.WARNING,
                "Failed to start Heatmap Dashboard",
                correlation_id=self._correlation_id,
                error=str(exc)
            )

    def stop(self) -> None:
        """Terminate the Heatmap Dashboard subprocess."""
        if self._process is None:
            return

        from config.logging_config import log_with_correlation

        log_with_correlation(
            self._logger, logging.INFO,
            "Stopping Heatmap Dashboard",
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
            if self._stderr_file is not None:
                try:
                    self._stderr_file.close()
                except Exception:
                    pass
                self._stderr_file = None
            self._process = None

    def is_running(self) -> bool:
        """Check if the heatmap subprocess is running."""
        if self._process is None:
            return False
        return self._process.poll() is None
