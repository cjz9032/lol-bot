import sys
import os
import time

# Add the project root to Python path for imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lolbot.bridge.server import start_bridge_server

def main():
    print('Starting bridge server...')
    server_thread = start_bridge_server()
    
    print('\nServer is running. Press Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nShutting down...')
        sys.exit(0)

if __name__ == '__main__':
    main()