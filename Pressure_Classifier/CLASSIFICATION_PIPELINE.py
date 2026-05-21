import os
import time
import csv
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import sys
import threading
import signal

# -------------------- Configuration
SAVE_DIR = "timestamps"
LABELS = ["l0", "l50", "l100", "f0", "f50", "f100", "r0", "r50", "r100"]
SAMPLES_PER_LABEL = 10      # how many samples per label will be recorded
TIME_BETWEEN_SAMPLES = 1.5  # seconds
LABEL_DISPLAY = {
    "l0": "Resting position",
    "f0": "Resting position",
    "r0": "Resting position",
    "l50": "Left 50%",
    "l100": "Left 100%",
    "f50": "Front 50%",
    "f100": "Front 100%",
    "r50": "Right 50%",
    "r100": "Right 100%",
}


class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Procedure")
        self.root.configure(bg="white")
        self.root.geometry("1000x600")

        self.current_label_index = 0
        self.current_sample = 0
        self.all_data = []
        self.user = None
        self.save_path = None
        self.waiting_for_space = False
        self.waiting_to_train = False
        self.training_in_progress = False
        self.waiting_for_ip_setup = False

        os.makedirs(SAVE_DIR, exist_ok=True)

        self.top_label = tk.Label(
            root,
            text="",
            font=("Arial", 32, "bold"),
            bg="white",
            fg="black",
            wraplength=900,
            justify="center"
        )
        self.top_label.pack(expand=True)

        self.bottom_label = tk.Label(
            root,
            text="",
            font=("Arial", 20),
            bg="white",
            fg="black",
            wraplength=900,
            justify="center"
        )
        self.bottom_label.pack(expand=True)

        self.root.bind("<space>", self.on_space)

        self.online_process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.ask_user()

    def ask_user(self):
        self.root.update()
        user_input = simpledialog.askstring("User", "Enter current user number:", parent=self.root)

        if not user_input or not user_input.strip():
            messagebox.showerror("Invalid input", "You must enter a valid user number.")
            self.root.destroy()
            return

        self.user = user_input.strip()
        filename = f"Timestamps_pressure_user_{self.user}.csv"
        self.save_path = os.path.join(SAVE_DIR, filename)

        self.set_text(
            "Prepare to start the training procedure",
            "The training will begin shortly."
        )
        self.root.after(5000, self.start_next_label)

    def set_text(self, top, bottom="", color="black"):
        self.top_label.config(text=top, fg=color)
        self.bottom_label.config(text=bottom, fg="black")
        self.root.update()

    def start_next_label(self):
        if self.current_label_index >= len(LABELS):
            self.finish_recording()
            return

        current_label = LABELS[self.current_label_index]
        self.countdown(current_label, 3)

    def countdown(self, label, count):
        if count > 0:
            display_label = LABEL_DISPLAY[label]
            self.set_text(
                f"Next movement: {display_label}",
                f"Starting in {count}...",
                color="black"
            )
            self.root.after(1000, lambda: self.countdown(label, count - 1))
        else:
            self.current_sample = 0
            self.record_sample()

    def record_sample(self):
        current_label = LABELS[self.current_label_index]
        display_label = LABEL_DISPLAY[current_label]

        timestamp = time.time()
        self.all_data.append([current_label, timestamp])
        self.current_sample += 1

        self.set_text(
            f"Current movement: {display_label}",
            f"Sample {self.current_sample}/{SAMPLES_PER_LABEL}\nTimestamp saved: {timestamp}",
            color="green"
        )

        if self.current_sample < SAMPLES_PER_LABEL:
            delay_ms = int(TIME_BETWEEN_SAMPLES * 1000)
            self.root.after(delay_ms, self.record_sample)
        else:
            self.label_completed()

    def label_completed(self):
        current_label = LABELS[self.current_label_index]

        if self.current_label_index < len(LABELS) - 1:
            next_label = LABELS[self.current_label_index + 1]
            self.waiting_for_space = True
            display_next = LABEL_DISPLAY[next_label]
            display_current = LABEL_DISPLAY[current_label]

            self.set_text(
                f"Next movement: {display_next}",
                f"{display_current} completed.\n\nPress SPACEBAR when you're ready to continue.",
                color="black"
            )
        else:
            self.finish_recording()

    def finish_recording(self):
        self.save_data()
        self.waiting_to_train = True
        self.set_text(
            "Recording finished",
            "Now, stop the OpenBCI session and save the data.\nWhen done, press SPACE to train the model.",
            color="black"
        )

    def on_space(self, event):
        if self.training_in_progress:
            return

        if self.waiting_for_space:
            self.waiting_for_space = False
            self.current_label_index += 1
            self.start_next_label()

        elif self.waiting_to_train:
            self.waiting_to_train = False
            self.start_model_training()

        elif self.waiting_for_ip_setup:
            self.waiting_for_ip_setup = False

            self.set_text(
                "Set the Quest IP",
                "Enter the Quest IP to start online classification.",
                color="black"
            )

            self.root.after(100, self.ask_IP)


    def save_data(self):
        with open(self.save_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["label", "timestamp"])
            writer.writerows(self.all_data)

    # --------------------------------------------------------------------------------- 
    # MODEL TRAINER FUNCTIONS
    # ---------------------------------------------------------------------------------

    def start_model_training(self):
        self.training_in_progress = True
        self.set_text(
            "Training model",
            "Don't close the window.",
            color="black"
        )

        training_thread = threading.Thread(target=self.run_model_trainer, daemon=True)
        training_thread.start()

    def run_model_trainer(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            trainer_path = os.path.join(script_dir, "Model_trainer.py")

            if not os.path.exists(trainer_path):
                raise FileNotFoundError(f"Could not find Model_trainer.py at {trainer_path}")

            subprocess.run(
                [sys.executable, trainer_path, str(self.user)],
                check=True
            )

            self.root.after(0, self.training_finished)

        except subprocess.CalledProcessError as e:
            self.root.after(0, lambda: self.training_failed(
                f"Model_trainer.py exited with error code {e.returncode}."
            ))
        except Exception as e:
            self.root.after(0, lambda: self.training_failed(str(e)))

    def training_finished(self):
        self.training_in_progress = False
        self.waiting_for_ip_setup = True

        self.set_text(
            "Now, start the OpenBCI session with UDP",
            "Press SPACEBAR to continue.",
            color="black"
        )

    def training_failed(self, error_message):
        self.training_in_progress = False
        self.set_text(
            "Training failed",
            error_message,
            color="black"
        )
        messagebox.showerror("Error", f"Training failed.\n\n{error_message}")

    # --------------------------------------------------------------------------------- 
    # ONLINE CLASSIFICATION FUNCTIONS
    # ---------------------------------------------------------------------------------

    # when the model finishes training, it asks the user the Quest IP
    # Then, it runs the online classification script with the IP and the user ID as arguments. 
    # The GUI will still show that the online classification is in process. 
    # if the GUI is closed, the online classification also terminates.

    def ask_IP(self):
        ip = simpledialog.askstring(
            "Quest IP",
            "Enter the Quest IP address (for example: 127.0.0.1):",
            parent=self.root
        )

        if not ip or not ip.strip():
            self.set_text(
                "Training finished",
                "The model has been trained successfully.\n\nOnline classification was not started.",
                color="black"
            )
            return

        ip = ip.strip()
        self.start_online_classification(ip)

    def start_online_classification(self, ip):
        self.set_text(
            "Online classification in progress",
            f"Connected to IP: {ip}\nDo not close the window unless you want to stop classification.",
            color="black"
        )

        thread = threading.Thread(
            target=self.run_online_classification,
            args=(ip,),
            daemon=True
        )
        thread.start()

    def run_online_classification(self, ip):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            online_path = os.path.join(script_dir, "Online_classification.py")

            if not os.path.exists(online_path):
                raise FileNotFoundError(f"Could not find Online_classification.py at {online_path}")

            self.online_process = subprocess.Popen(
                [sys.executable, online_path, ip, str(self.user)],
                cwd=script_dir
            )

            return_code = self.online_process.wait()
            self.online_process = None

            if return_code == 0:
                self.root.after(0, lambda: self.set_text(
                    "Online classification finished",
                    "The online classification process ended.",
                    color="black"
                ))
            else:
                self.root.after(0, lambda: self.set_text(
                    "Online classification stopped",
                    f"The process ended with code {return_code}.",
                    color="black"
                ))

        except Exception as e:
            self.online_process = None
            self.root.after(0, lambda: self.training_failed(str(e)))

    def on_close(self):
        try:
            if self.online_process is not None:
                if self.online_process.poll() is None:
                    self.online_process.terminate()
                    try:
                        self.online_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.online_process.kill()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = TrainingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()