import socket

UNITY_IP = "10.26.30.182"  # pc: 127.0.0.1, quest: 10.173.32.182
UNITY_PORT = 5052

# Map numpad keys to messages
key_map = {
    '1': (0.25, [8, 0, 0]),
    '2': (0.25, [0, 8, 0]),
    '3': (0.2, [0, 0, 8]),
    '4': (0.6, [60, 0, 0]),
    '5': (0.5, [0, 60, 0]),
    '6': (0.5, [0, 0, 60]),
    '7': (0.8, [90, 0, 0]),
    '8': (0.9, [0, 90, 0]),
    '9': (0.9, [0, 0, 90])
}

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Press numpad keys to send data to Unity. Type 'esc' to quit.")

try:
    while True:
        key = input("Key: ").strip()

        if key.lower() == 'esc':
            print("Exiting...")
            break

        if key in key_map:
            label, pressure = key_map[key]
            message = f"{label},{pressure[0]},{pressure[1]},{pressure[2]}"
            try:
                sock.sendto(message.encode('utf-8'), (UNITY_IP, UNITY_PORT))
                print(f"Sent: {message}")
            except Exception as e:
                print(f"Error sending UDP message: {e}")
        else:
            print("Invalid key. Use numbers 1-9 or 'esc'.")

except KeyboardInterrupt:
    print("\nStopped by user.")

sock.close()
