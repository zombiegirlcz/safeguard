"""
Storage module for safeguard.

Handles persistent storage of media usage events using SQLite.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass, asdict

from .monitors import MediaUsageEvent, MediaType


class MediaStorage:
    """SQLite-based storage for media usage events."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_dir = Path.home() / ".safeguard"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "media_history.db"

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                application_name TEXT NOT NULL,
                media_type TEXT NOT NULL,
                process_id INTEGER NOT NULL,
                is_active INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def store_event(self, event: MediaUsageEvent) -> int:
        """Store a media usage event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO media_events (timestamp, application_name, media_type, process_id, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.application_name,
                event.media_type.value,
                event.process_id,
                1 if event.is_active else 0
            )
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_events(self, hours: int = 24) -> List[MediaUsageEvent]:
        """Get media usage events from the last N hours."""
        since = datetime.now() - timedelta(hours=hours)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, application_name, media_type, process_id, is_active
            FROM media_events
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            """,
            (since.isoformat(),)
        )

        events = []
        for row in cursor.fetchall():
            timestamp_str, app_name, media_type_str, pid, is_active = row
            event = MediaUsageEvent(
                timestamp=datetime.fromisoformat(timestamp_str),
                application_name=app_name,
                media_type=MediaType(media_type_str),
                process_id=pid,
                is_active=bool(is_active)
            )
            events.append(event)

        conn.close()
        return events

    def get_summary(self, hours: int = 24) -> dict:
        """Get summary statistics for media usage."""
        events = self.get_events(hours)

        app_usage = {}
        media_type_usage = {}

        for event in events:
            # Track per-application usage
            if event.application_name not in app_usage:
                app_usage[event.application_name] = {
                    'count': 0,
                    'microphone': 0,
                    'camera': 0
                }
            app_usage[event.application_name]['count'] += 1
            if event.media_type == MediaType.MICROPHONE:
                app_usage[event.application_name]['microphone'] += 1
            else:
                app_usage[event.application_name]['camera'] += 1

            # Track per-media-type usage
            if event.media_type not in media_type_usage:
                media_type_usage[event.media_type.value] = 0
            media_type_usage[event.media_type.value] += 1

        return {
            'total_events': len(events),
            'applications': app_usage,
            'media_types': media_type_usage,
            'time_period_hours': hours
        }

    def clear_events(self, older_than_days: int = 30):
        """Clear events older than specified days."""
        cutoff = datetime.now() - timedelta(days=older_than_days)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM media_events WHERE timestamp < ?",
            (cutoff.isoformat(),)
        )
        conn.commit()
        conn.close()
