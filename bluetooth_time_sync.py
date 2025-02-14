#!/usr/bin/env python3
import bluetooth
import os
import time

def set_pi_time(new_time):
    """Update Raspberry Pi system time."""
    try:
        os.system(f"sudo date -s '{new_time}'")  # Updates the system clock
        print(f"✅ System time updated to: {new_time}")
    except Exception as e:
        print(f"⚠️ Failed to update time: {e}")

def disconnect_bluetooth(client_address):
    """Force disconnect Bluetooth after 15 seconds."""
    print(f"🔌 Auto-disconnecting {client_address} after 15 seconds...")
    time.sleep(15)  # Wait 15 seconds
    os.system(f"bluetoothctl disconnect {client_address}")  # Disconnect
    print(f"❌ Disconnected {client_address}")

def bluetooth_server():
    """Sets up a Bluetooth server to receive time data from a phone."""
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)

    print("📡 Waiting for a Bluetooth connection...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"🔗 Connected to {client_address}")

        try:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if data:
                print(f"📩 Received time: {data}")
                set_pi_time(data)  # Update system time
        except Exception as e:
            print(f"⚠️ Error receiving data: {e}")

        client_socket.close()

        # Start auto-disconnect after 15 seconds
        disconnect_bluetooth(client_address[0])
