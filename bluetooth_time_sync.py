#!/usr/bin/env python3
import bluetooth
import os
import time
import subprocess

def set_pi_time(new_time):
    """Update Raspberry Pi system time using 'date -s'."""
    try:
        cmd = f"sudo date -s '{new_time}'"
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ System time updated to: {new_time}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to update system time: {e}")

def disconnect_bluetooth(client_address):
    """Force disconnect Bluetooth after 15 seconds."""
    print(f"🔌 Auto-disconnecting {client_address} after 15 seconds...")
    time.sleep(15)
    os.system(f"bluetoothctl disconnect {client_address}")
    print(f"❌ Disconnected {client_address}")

def bluetooth_server():
    """
    Sets up an RFCOMM-based (SPP) Bluetooth server to receive time data.
    Use an Android app like 'Serial Bluetooth Terminal' to connect and send
    a string (e.g. '2025-02-20 10:30:00').
    """

    # 1. Create an RFCOMM socket and bind it
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)

    # 2. Advertise our Serial Port service (SPP)
    port = server_socket.getsockname()[1]
    service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"  # Example UUID
    bluetooth.advertise_service(
        server_socket,
        "TimeSyncService",           # Service name
        service_id=service_uuid,
        service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print(f"📡 SPP server waiting on RFCOMM channel {port}...")
    print("🔎 Ensure your Pi is discoverable and pairable (see bluetoothctl settings).")
    print("When connected via a Bluetooth terminal app, send a time string to set the Pi's clock.")

    while True:
        print("📡 Waiting for a Bluetooth connection...")
        client_socket, client_address = server_socket.accept()
        print(f"🔗 Connected to {client_address}")

        try:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if data:
                print(f"📩 Received time: {data}")
                set_pi_time(data)
        except Exception as e:
            print(f"⚠️ Error receiving data: {e}")

        client_socket.close()
        disconnect_bluetooth(client_address[0])
