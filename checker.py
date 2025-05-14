import argparse
import requests
import re

def parse_m3u(m3u_file):
    with open(m3u_file, 'r', encoding='iso-8859-1', errors="ignore") as f:
        m3u_content = f.read()
    channels = re.findall(r'#EXTINF:.*?,(.*?)\n(.*?)\n', m3u_content)
    return channels

def is_valid_url(url):
    return url.startswith('http://') or url.startswith('https://')

def handle_status_code(status_code, name):
    status_messages = {
        403: '403 : Server is not OK :(',
        404: '404 : Server is not OK :(',
        500: '500 : Server is not OK :(',
        503: '503 : Server is not OK :(',
        504: '504 : Server is not OK :(',
        200: f'Channel {name} is Ok :)'
    }
    if status_code in status_messages:
        print(status_messages[status_code])
        return status_code == 200
    else:
        print('???')
        return False

def check_channels(channels):
    server_ok = False
    for name, url in channels:
        print(f'Checking channel: {name} - {url}')
        if not is_valid_url(url):
            print("⚠ Channel link is bad, skipping channel")
            continue
        print("⚠ Channel link is fine")
        try:
            r = requests.get(url, timeout=5)
            server_ok = handle_status_code(r.status_code, name)
        except requests.exceptions.Timeout:
            print("⚠ Server is slow, skipping channel")
        except requests.exceptions.TooManyRedirects:
            print("⚠ Channel link is bad, skipping channel")
        except Exception as e:
            print("===== FATAL ERROR =====")
            print(e)
    return server_ok


def main():
    parser = argparse.ArgumentParser(description='Extract accessible channels from M3U playlist')
    
    parser.add_argument('-l', '--local', help='Path to local M3U file')

    args = parser.parse_args()

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
