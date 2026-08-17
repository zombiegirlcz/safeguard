# Safeguard

Real-time monitoring of microphone and camera usage by applications on Windows.

## Features

- Real-time monitoring of microphone and camera usage
- Persistent logging of media usage history
- CLI interface for easy use
- SQLite-based storage for usage events

## Installation

```bash
uv pip install .
```

## Usage

```bash
uv run safeguard
```

Or directly:

```bash
python -m safeguard.main
```

## Building

```bash
uv build
```

## Windows Requirements

- Windows 10 or later
- Python 3.10 or later
- Administrator privileges recommended for full monitoring
