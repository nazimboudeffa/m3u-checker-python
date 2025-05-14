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

def handle_status_code(status_code):
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
    
def check_stream(url):
    try:
        probe = ffmpeg.probe(url, v='error')
        if 'streams' in probe and len(probe['streams']) > 0:
            logging.info(f"Stream {url} is OK")
            return True
        else:
            logging.error(f"Stream {url} is not valid")
            return False
    except ffmpeg.Error as e:
        logging.error(f"Error checking stream {url}: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False

def capture_frame(url, file_name, output_path="captures"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    command = [
        'ffmpeg', '-y', '-i', url, '-ss', '00:00:02', '-frames:v', '1',
        os.path.join(output_path, f"{file_name}.png")
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        logging.debug(f"Screenshot saved for {file_name}")
        return True
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout when trying to capture frame for {file_name}")
        return False
    
def check_single_channel(name, url):
    if not is_valid_url(url):
        logging.info(f"Channel {name} url is bad, skipping channel")
        return False
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            logging.info(f"Channel {name} is OK")
            if check_stream(url):
                logging.info(f"Stream {name} is valid")
                if capture_frame(url, name):
                    logging.info(f"Screenshot captured for {name}")
                else:
                    logging.error(f"Failed to capture screenshot for {name}")
            else:
                logging.error(f"Stream {name} is not valid")
            return True
        else:
            status_message = handle_status_code(r.status_code)
            logging.info(f"Channel {name} returned status: {status_message}")
    except requests.exceptions.Timeout:
        logging.error("⚠ Server is slow, skipping channel")
    except requests.exceptions.TooManyRedirects:
        logging.error("⚠ Channel link is bad, skipping channel")
    except Exception:
        logging.error("===== FATAL ERROR =====")
    return False

def check_channels(channels):
    server_ok = False
    for name, url in channels:
        if check_single_channel(name, url):
            server_ok = True
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
