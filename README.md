# M3U Checker

This is a Python script that checks an m3u file

# Installation

On Windows install ffmpeg and add bin folder in PATH from https://ffmpeg.org/download.html


## Prerequisites

- **Python 3.13+**
- **ffmpeg** and **ffprobe**: Required for capturing screenshots and retrieving stream information.

## Clone the Repository

```bash
git clone https://github.com/nazimboudeffa/m3u-checker-python.git
cd m3u-checker-python
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

# Usage

```bash
python checker.py -l path/to/local.m3u
```

- **`-v`**: Increase output verbosity to `INFO` level.
- **`-vv`**: Increase output verbosity to `DEBUG` level.

