#!/usr/bin/env python3
import threading
from bluetooth_time_sync import bluetooth_server
from bible_clock import bible_clock_loop

if __name__ == '__main__':
    # Start the Bluetooth server in a background thread.
    bt_thread = threading.Thread(target=bluetooth_server(), daemon=True)
    bt_thread.start()

    # Run the Bible Clock display loop in the main thread.
    bible_clock_loop()
