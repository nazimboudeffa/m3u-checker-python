import argparse
import requests
import re
import os
import logging
import subprocess
import ffmpeg

# Set up logging
def setup_logging(verbose_level):
    if verbose_level == 1:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    elif verbose_level >= 2:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Only critical errors will be logged by default.

def parse_m3u(m3u_file):
    with open(m3u_file, 'r', encoding='iso-8859-1', errors="ignore") as f:
        m3u_content = f.read()
    channels = re.findall(r'#EXTINF:.*?,(.*?)\n(.*?)\n', m3u_content)
    return channels

def is_valid_url(url):
    return url.startswith('http://') or url.startswith('https://')

def handle_status_code(status_code, name):
    status_messages = {
        301: "Moved Permanently",
        302: "Found",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }
    if status_code in status_messages:
        return status_messages[status_code]
    else:
        return "Unknown status"
    
def check_channels(channels):
    server_ok = False
    for name, url in channels:
        if not is_valid_url(url):
            logging.info("⚠ Channel url is bad, skipping channel")
            continue
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                server_ok = True
                logging.info(f"Channel {name} is OK")
            else:
                status_message = handle_status_code(r.status_code, name)
                logging.info(f"Channel {name} returned status: {status_message}")
        except requests.exceptions.Timeout:
            logging.error("⚠ Server is slow, skipping channel")
        except requests.exceptions.TooManyRedirects:
            logging.error("⚠ Channel link is bad, skipping channel")
        except Exception as e:
            logging.error("===== FATAL ERROR =====")
    return server_ok


def main():
    parser = argparse.ArgumentParser(description='Extract accessible channels from M3U playlist')   
    parser.add_argument('-l', '--local', help='Path to local M3U file')
    args = parser.parse_args()
    setup_logging(1)
    if args.local:
        m3u_file = args.local
    else:
        parser.error('Please specify a local M3U file')
        exit()

    print(r"""
    --------------------------
    STREAMING CHANNELS CHECKER
    --------------------------                                                                                                                                     
    """)
    channels = parse_m3u(m3u_file)
    check_channels(channels)

if __name__ == '__main__':
    main()
