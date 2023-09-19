import cv2
import pytesseract
import numpy as np
import pandas as pd
import threading
from matplotlib import pyplot as plt
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import Tk
from PIL import Image

cap = None  # define cap as a global variable
x, y, w, h = 0, 0, 0, 0

def get_video_file_path():
    global cap
    root = Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename()
    cap = cv2.VideoCapture(file_path)  # initialize cap with the selected video file
    root.destroy()
    return file_path

def get_output_dir():
    root = Tk()
    root.withdraw() 
    output_dir = filedialog.askdirectory()
    root.destroy()
    return output_dir

def get_frame_rate():
    root = Tk()
    root.withdraw() 
    frame_rate = simpledialog.askfloat("Input", "What frame rate do you want?")
    root.destroy()
    return frame_rate

def select_roi():
    global cap, x, y, w, h
    ret, frame = cap.read()
    r = cv2.selectROI(frame)
    x, y, w, h = map(int, r)
    cv2.destroyAllWindows()
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

def process_video(video_file_path, frame_rate, output_dir):
    global cap, x, y, w, h
    FPS = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = int(FPS / frame_rate)
    all_numbers = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        roi = frame[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi, config='--psm 6')
        numbers = [float(s) for s in text.split() if is_float(s)]
        all_numbers.extend(numbers)
        for _ in range(frame_skip):
            if not cap.read()[0]:
                break
    cap.release()
    df = pd.DataFrame(all_numbers, columns=['Values'])
    df.to_csv(f"{output_dir}/output.csv", index=False)

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def start_processing():
    video_file_path = get_video_file_path()
    output_dir = get_output_dir()
    frame_rate = get_frame_rate()
    select_roi()
    thread = threading.Thread(target=process_video, args=(video_file_path, frame_rate, output_dir))
    thread.start()

start_processing()
