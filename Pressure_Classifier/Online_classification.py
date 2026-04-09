import numpy as np
import requests
import time
import joblib
from scipy.signal import butter, filtfilt, iirnotch, hilbert, find_peaks
from pykalman import KalmanFilter
import pywt
import pandas as pd
import tkinter as tk
from tkinter import ttk
import threading
import socket
import json 
import sys
import os

# Online settings
if len(sys.argv) < 3:
    raise ValueError("Expected arguments: <ip> <user>")

UNITY_IP = sys.argv[1] # pc: 127.0.0.1
user = sys.argv[2]

JITTER_NOMALIZATION = 0.9         # <1 to increase the max, >1 to decrease the max
PRESSURE_NORMALIZATION = 1      # <1 to increase the max, >1 to decrease the max

# ---------------- Settings ----------------
USE_BANDPASS = 1
USE_NOTCH = 1
USE_HILBERT = 1
USE_KALMAN = 0
USE_TKEO = 0
USE_ENVELOPE = 0
USE_ZSCORE = 0
USE_SCALING = 1

HOP_SECONDS = 0.2

sampling_rate = 250
window_size_seconds = 1.25 
window_size_samples = int(window_size_seconds * sampling_rate)

MAX_JITTERING = 250

# OPEN BCI SETTINGS
UDP_IP = "127.0.0.1"  
UDP_PORT1 = 12345  
UDP_PORT2 = 12346
channels = ['ch_1', 'ch_2', 'ch_3']

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1.bind((UDP_IP, UDP_PORT1))

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind((UDP_IP, UDP_PORT2))

# UDP communication
UNITY_PORT = 5052
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ---------------- Filters -----------------
def bandpass_filter(data, lowcut=5.0, highcut=120.0, fs=sampling_rate, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def notch_filter(signal, freq=50.0, fs=sampling_rate, quality=30):
    nyquist = 0.5 * fs
    norm_freq = freq / nyquist
    b, a = iirnotch(norm_freq, quality)
    return filtfilt(b, a, signal)

def hilbert_envelope(signal):
    analytic = hilbert(signal)
    return np.abs(analytic)

def kalman(signal):
    signal = signal.reshape(-1, 1)
    kf = KalmanFilter(transition_matrices=[1],
                      observation_matrices=[1],
                      initial_state_mean=0,
                      observation_covariance=0.01,
                      transition_covariance=1e-5)
    state_means, _ = kf.filter(signal)
    return state_means.flatten()

def tkeo(signal):
    output = np.zeros_like(signal)
    for i in range(1, len(signal) - 1):
        output[i] = signal[i]**2 - signal[i - 1] * signal[i + 1]
    return output

# ---------------- Feature extraction ----------------
def rms(signal):
    return np.sqrt(np.mean(signal**2))

def rms_signed_difference(signal):
    mean_val = np.mean(signal)
    diff = signal - mean_val
    return np.sqrt(np.mean(diff**2))

def zero_crossings(signal):
    signs = np.signbit(signal)
    return np.sum(signs[1:] != signs[:-1])

def waveform_length(signal):
    return np.sum(np.abs(np.diff(signal)))

def mav(signal):
    return np.mean(np.abs(signal))

def iav(signal):
    return np.sum(np.abs(signal))

def mean_frequency(signal, fs=sampling_rate):
    freqs = np.fft.rfftfreq(len(signal), d=1/fs)
    fft_vals = np.abs(np.fft.rfft(signal))
    power = fft_vals**2
    if np.sum(power) == 0:
        return 0
    return np.sum(freqs * power) / np.sum(power)

def extract_features(window):
    feature_names = ['RMS', 'RMS_SD', 'ZC', 'WL', 'MAV', 'STD', 'VAR', 'IAV', 'MF']
    feats = []
    for ch_idx in range(len(channels)):
        ch_signal = window[:, ch_idx]
        feats.extend([
            rms(ch_signal),
            rms_signed_difference(ch_signal),
            zero_crossings(ch_signal),
            waveform_length(ch_signal),
            mav(ch_signal),
            np.std(ch_signal),
            np.var(ch_signal),
            iav(ch_signal),
            mean_frequency(ch_signal)
        ])
    cols = [f"{ch}_{feat}" for ch in channels for feat in feature_names]
    return pd.DataFrame([feats], columns=cols)


# ---------------- Data acquisition ----------------

def get_data1():
    """
    Receive data packets from UDP socket, parse JSON, and extract channel samples.
    Return a list of tuples: [(ch1_sample1, ch2_sample1, ch3_sample1), (ch1_sample2, ch2_sample2, ch3_sample2), ...]
    """
    try:
        data, addr = sock1.recvfrom(4096)  
        packet = json.loads(data.decode())
        
        if 'data' in packet:
            channel_data = packet['data']  # expected to be a list of lists, one per channel
            
            ch1 = channel_data[0]
            ch2 = channel_data[1]
            ch3 = channel_data[2]
            
            # zip samples by index
            samples = list(zip(ch1, ch2, ch3))
            return samples
        
    except Exception as e:
        # If no data or error, just return empty list and continue
        print(f"Error receiving or parsing UDP data: {e}")
        return []
    
    return []

def get_data2():
    try:
        data, addr = sock2.recvfrom(4096)  
        packet = json.loads(data.decode())
        
        if 'data' in packet:
            joystick_data = packet['data']  # expected to be a list of lists, one per channel
            return joystick_data[0]
        
    except Exception as e:
        # If no data or error, just return empty list and continue
        print(f"Error receiving or parsing UDP data: {e}")
        return []
    
    return []


# ---------------- Main online classification ----------------

def classification_loop():

    # Load models and scalers
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "models")
    pressure_regressor = joblib.load(f"{model_dir}/Pressure_regressor_user_{user}.joblib")  # whole pipeline already included

    # Buffers for data
    buffer = [] 

    print(f"Starting online classification with window size {window_size_seconds}s ({window_size_samples} samples)...")

    HOP_SAMPLES = int(HOP_SECONDS * sampling_rate)
    jitter = 0.0

    while True:
        new_data = get_data1()
        jitter = get_data2()

        if not new_data:
            time.sleep(0.1)
            continue

        buffer.extend(new_data)

        # If buffer full enough
        if len(buffer) >= window_size_samples: 
            window = np.array(buffer[:window_size_samples])
            buffer = buffer[HOP_SAMPLES:]  # remove the first HOP_SAMPLES samples

            # Apply filtering channel-wise
            for i in range(window.shape[1]):
                if i in [0,1,2]:
                    if USE_NOTCH == 1:
                        window[:, i] = notch_filter(window[:, i], fs=sampling_rate)
                    if USE_BANDPASS == 1:
                        window[:, i] = bandpass_filter(window[:, i])
                    if USE_HILBERT == 1:
                        window[:, i] = hilbert_envelope(window[:, i])
                    if USE_KALMAN == 1:
                        window[:, i] = kalman(window[:, i])
                    if USE_TKEO == 1:
                        window[:, i] = tkeo(window[:, i])
                    if USE_ENVELOPE == 1:
                        # can use compute_envelope_peaks or compute_envelope
                        pass
                    if USE_ZSCORE == 1:
                        mean = window[:, i].mean()
                        std = window[:, i].std() if window[:, i].std() != 0 else 1
                        window[:, i] = (window[:, i] - mean) / std

            # Jittering detection
            jittering = np.max(np.abs(window)) / MAX_JITTERING # absolute values because the signal is bipolar
            jitter_init = jitter
            jitter = jitter/JITTER_NOMALIZATION
            #print(jittering)
            #print(jittering, jitter)
            print(jitter_init, " + ", jitter)

            # Extract features
            feats = extract_features(window)
            feats_pressure = feats

            # Predict pressure
            pressure_pred = pressure_regressor.predict(feats_pressure)

            # Keep only the highest pressure, set others to 0, and normalize
            pressure_pred = pressure_pred[0]  
            max_idx = np.argmax(pressure_pred)
            filtered_pressure = np.zeros_like(pressure_pred)
            filtered_pressure[max_idx] = pressure_pred[max_idx]
            filtered_pressure = filtered_pressure / PRESSURE_NORMALIZATION

            # Print filtered/final predictions
            print(f"--Filtered Pressure prediction: {filtered_pressure}")

            # Send filtered pressure to Unity as a string like: "jittering,pressure", "37,50,0,0"
            pressure_values = [int(p) for p in filtered_pressure]  
            message = f"{jitter},{pressure_values[0]},{pressure_values[1]},{pressure_values[2]}"
            try:
                udp_socket.sendto(message.encode('utf-8'), (UNITY_IP, UNITY_PORT))
            except Exception as e:
                print(f"Error sending UDP message: {e}")

        else:
            # Sleep shortly to avoid busy loop
            time.sleep(0.01)

if __name__ == "__main__":
    classification_loop()
