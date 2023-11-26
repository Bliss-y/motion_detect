import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image as PilImage, ImageTk as PilImageTk
import threading
import queue
from detector import detect_cap as detect_motion
import numpy as np
from queue import Empty

motion_queue = queue.Queue()

def update_motion_label(label, motion_queue):
    while True:
        try:
            frame = motion_queue.get(timeout=1)
            resized_frame = cv2.resize(frame, (200, 200))
            pil_image = PilImage.fromarray(resized_frame)
            tk_image = PilImageTk.PhotoImage(pil_image)
            label.tk_image = tk_image
            label.config(image=tk_image)
        except Empty:
            pass

def process_motion(cap, motion_queue):
    detect_motion(cap, motion_queue)

root = tk.Tk()
root.title("Motion Detection Camera")
root.geometry("800x600")
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

frame = tk.Frame(canvas, width=800, height=800)
frame.pack(expand=True)
canvas.create_window((0, 0), window=frame, anchor="nw")

motion_labels = []
caps = []
threads = []

for i in range(2):
    f = ttk.Frame(frame)
    motion_label = ttk.Label(frame)
    motion_label.pack(padx=10, pady=10)
    motion_labels.append(motion_label)
    cap = cv2.VideoCapture(i)
    caps.append(cap)
    motion_queue_for_feed = queue.Queue()
    motion_thread = threading.Thread(target=process_motion, args=(cap, motion_queue_for_feed))
    motion_thread.daemon = True
    motion_thread.start()
    threads.append(motion_thread)
    label_thread = threading.Thread(target=update_motion_label, args=(motion_label, motion_queue_for_feed))
    label_thread.daemon = True
    label_thread.start()

horizontal_scrollbar = ttk.Scrollbar(canvas, orient="horizontal", command=canvas.xview)
vertical_scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
canvas.configure(xscrollcommand=horizontal_scrollbar.set, yscrollcommand=vertical_scrollbar.set)
horizontal_scrollbar.pack(side="bottom", fill="x")
vertical_scrollbar.pack(side="right", fill="y")
canvas.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

def close_window():
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()
    root.destroy()

exit_button = ttk.Button(root, text="Exit", command=close_window)
exit_button.pack(padx=10, pady=10)

root.mainloop()