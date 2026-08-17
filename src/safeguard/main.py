"""
Main entry point for the safeguard project.
"""

import asyncio
import sys


def main():
    """Main entry point for the safeguard CLI."""
    from .monitors import MediaMonitor
    from .logger import MediaLogger
    from .storage import MediaStorage

    print("Safeguard - Media Usage Monitor")
    print("Starting monitoring...")

    # Initialize components
    monitor = MediaMonitor()
    logger = MediaLogger()
    storage = MediaStorage()

    # Start monitoring
    asyncio.run(monitor.start_monitoring())


if __name__ == "__main__":
    main()
