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

# OPEN BCI SETTINGS
UDP_IP = "127.0.0.1"  
UDP_PORT = 12345  
channels = ['ch_1', 'ch_2', 'ch_3']

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def get_data():
    """
    Receive data packets from UDP socket, parse JSON, and extract channel samples.
    Return a list of tuples: [(ch1_sample1, ch2_sample1, ch3_sample1), (ch1_sample2, ch2_sample2, ch3_sample2), ...]
    """
    try:
        data, addr = sock.recvfrom(4096)  
        packet = json.loads(data.decode())
        print(packet)
        
    except Exception as e:
        # If no data or error, just return empty list and continue
        print(f"Error receiving or parsing UDP data: {e}")
        return []
    
    return []


def classification_loop():

    while True:
        new_data = get_data()

if __name__ == "__main__":
    classification_loop()
