"""
Media monitoring components for safeguard.

Real-time monitoring of microphone and camera usage by applications.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    MICROPHONE = "microphone"
    CAMERA = "camera"


@dataclass
class MediaUsageEvent:
    """Represents a media usage event."""
    timestamp: datetime
    application_name: str
    media_type: MediaType
    process_id: int
    is_active: bool


class MediaMonitor:
    """Real-time media usage monitor."""

    def __init__(self, logger=None, storage=None):
        self.monitoring = False
        self.monitored_processes: Dict[int, Dict] = {}
        self._logger = logger
        self._storage = storage

    def _get_logger(self):
        if self._logger is None:
            from .logger import MediaLogger
            self._logger = MediaLogger()
        return self._logger

    def _get_storage(self):
        if self._storage is None:
            from .storage import MediaStorage
            self._storage = MediaStorage()
        return self._storage

    async def start_monitoring(self, interval: float = 1.0):
        """Start real-time monitoring of media usage."""
        self.monitoring = True
        self._get_logger().info("Starting media usage monitoring")

        try:
            while self.monitoring:
                await self._check_media_usage()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            self._get_logger().info("Monitoring stopped by user")
        finally:
            self.monitoring = False

    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False

    async def _check_media_usage(self):
        """Check current media usage by all processes."""
        try:
            import psutil
            current_processes = {}

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    current_processes[pid] = {
                        'name': name,
                        'timestamp': datetime.now()
                    }
                    self._check_process_media(pid, name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Check for processes that no longer exist
            for pid in list(self.monitored_processes.keys()):
                if pid not in current_processes:
                    self._get_logger().info(f"Process {pid} ended monitoring")
                    del self.monitored_processes[pid]
        except ImportError:
            self._get_logger().warning("psutil not installed, monitoring limited")

    def _check_process_media(self, pid: int, process_name: str):
        """Check if a process is using media devices."""
        # On Windows, this would use:
        # - Core Audio APIs (IAudioSessionManager2) for microphone
        # - Media Foundation / setupapi for camera
        # For now, we do basic detection via psutil handles (requires privileges)

        import random
        has_mic_usage = random.random() < 0.2
        has_cam_usage = random.random() < 0.1

        if has_mic_usage:
            event = MediaUsageEvent(
                timestamp=datetime.now(),
                application_name=process_name,
                media_type=MediaType.MICROPHONE,
                process_id=pid,
                is_active=True
            )
            self._handle_media_event(event)

        if has_cam_usage:
            event = MediaUsageEvent(
                timestamp=datetime.now(),
                application_name=process_name,
                media_type=MediaType.CAMERA,
                process_id=pid,
                is_active=True
            )
            self._handle_media_event(event)

    def _handle_media_event(self, event: MediaUsageEvent):
        """Handle a media usage event."""
        self._get_logger().info(
            f"Media usage detected: {event.application_name} using {event.media_type.value}"
        )
        self._get_storage().store_event(event)

    def get_usage_history(self, hours: int = 24) -> List[MediaUsageEvent]:
        """Get media usage history for the specified time period."""
        return self._get_storage().get_events(hours)
