"""
Tests for safeguard project.
"""

import sys
import pytest
from datetime import datetime, timedelta


def test_version():
    """Test that version is defined."""
    from safeguard import __version__
    assert __version__ == "0.1.0"


def test_media_type_enum():
    """Test MediaType enum values."""
    from safeguard.monitors import MediaType
    assert MediaType.MICROPHONE.value == "microphone"
    assert MediaType.CAMERA.value == "camera"


def test_media_usage_event():
    """Test MediaUsageEvent creation."""
    from safeguard.monitors import MediaUsageEvent, MediaType
    now = datetime.now()
    event = MediaUsageEvent(
        timestamp=now,
        application_name="test_app",
        media_type=MediaType.MICROPHONE,
        process_id=1234,
        is_active=True
    )
    assert event.timestamp == now
    assert event.application_name == "test_app"
    assert event.media_type == MediaType.MICROPHONE
    assert event.process_id == 1234
    assert event.is_active is True


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
def test_storage_creation():
    """Test that storage can be created."""
    from safeguard.storage import MediaStorage
    storage = MediaStorage()
    assert storage.db_path is not None


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
def test_storage_event_storage():
    """Test storing and retrieving events."""
    from safeguard.storage import MediaStorage
    from safeguard.monitors import MediaUsageEvent, MediaType

    storage = MediaStorage()
    event = MediaUsageEvent(
        timestamp=datetime.now(),
        application_name="test_app",
        media_type=MediaType.CAMERA,
        process_id=1234,
        is_active=True
    )
    event_id = storage.store_event(event)
    assert event_id > 0

    events = storage.get_events(hours=1)
    assert len(events) >= 1
    assert events[0].application_name == "test_app"


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
def test_storage_summary():
    """Test storage summary generation."""
    from safeguard.storage import MediaStorage
    from safeguard.monitors import MediaUsageEvent, MediaType

    storage = MediaStorage()
    event = MediaUsageEvent(
        timestamp=datetime.now(),
        application_name="summary_test_app",
        media_type=MediaType.MICROPHONE,
        process_id=5678,
        is_active=True
    )
    storage.store_event(event)
    summary = storage.get_summary(hours=1)
    assert summary['total_events'] >= 1
    assert 'summary_test_app' in summary['applications']
