import socket
import tkinter as tk

# === CONFIG ===
UNITY_IP = "10.26.30.182"  # PC: 127.0.0.1, quest: 10.173.32.182, 10.86.78.182
UNITY_PORT = 5055
ADDRESS = (UNITY_IP, UNITY_PORT)

# === SOCKET ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === SEND FUNCTION ===
def send_command(value):
    try:
        msg = str(value).encode()
        sock.sendto(msg, ADDRESS)
        print(f"Sent: {value}")
    except Exception as e:
        print(f"Error sending: {e}")

# === UI SETUP ===
root = tk.Tk()
root.title("Send Commands to Unity")
# CHANGED: Increased height to fit new buttons
root.geometry("300x450") 

# === BUTTONS MAPPING ===
# CHANGED: Updated to match new Unity Duplicate Scenes (1-4) and Home (0)
buttons = [
    ("Frog Ego (Body)", 1),
    ("Frog Exo (Wasp)", 2),
    ("Kart Ego (Car)", 3),
    ("Kart Exo (World)", 4),
    ("Stop / Home", 5),
]

for text, value in buttons:
    tk.Button(root, text=text, font=("Arial", 12), width=25,
              command=lambda v=value: send_command(v)).pack(pady=5)

# === THRESHOLD SECTION ===
threshold_frame = tk.Frame(root)
threshold_frame.pack(pady=10)

tk.Label(threshold_frame, text="Thresholds:", font=("Arial", 12)).grid(row=0, column=0, columnspan=3, pady=(0, 5))

# Default values for convenience
entry1 = tk.Entry(threshold_frame, width=5)
entry1.insert(0, "5")
entry2 = tk.Entry(threshold_frame, width=5)
entry2.insert(0, "33")
entry3 = tk.Entry(threshold_frame, width=5)
entry3.insert(0, "66")

entry1.grid(row=1, column=0, padx=5)
entry2.grid(row=1, column=1, padx=5)
entry3.grid(row=1, column=2, padx=5)

def send_thresholds():
    try:
        t1 = int(entry1.get())
        t2 = int(entry2.get())
        t3 = int(entry3.get())
        threshold_string = f"{t1},{t2},{t3}"
        send_command(threshold_string)
        print(f"Sent Thresholds: {threshold_string}")
    except ValueError:
        print("Invalid threshold input. Please enter numbers.")

tk.Button(root, text="Update Thresholds", font=("Arial", 11), width=25,
          command=send_thresholds).pack(pady=10)

# === CLOSE SOCKET ON EXIT ===
def on_close():
    print("Closing socket...")
    sock.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()