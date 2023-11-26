import os
import subprocess
import tkinter as tk
from tkinter import ttk
from moviepy.editor import VideoFileClip, concatenate_videoclips

def list_files_and_folders(directory):
    files_and_folders = os.listdir(directory)
    folders = []
    mp4_files = []

    for item in files_and_folders:
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item)
        elif item.lower().endswith(".mp4"):
            mp4_files.append(item)

    return folders, mp4_files

def play_video(file_path):
    try:
        subprocess.run(["start", file_path], shell=True)
    except Exception as e:
        print(f"Error playing video: {e}")

def combine_and_delete_mp4_files(folder_path):
    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]
    if len(mp4_files) < 2:
        return

    video_clips = [VideoFileClip(os.path.join(folder_path, mp4)) for mp4 in mp4_files]
    combined_clip = concatenate_videoclips(video_clips, method="compose")
    combined_file = os.path.join(folder_path, "combined.mp4")
    combined_clip.write_videofile(combined_file, codec="libx264")

    for mp4 in mp4_files:
        os.remove(os.path.join(folder_path, mp4))

    refresh_list()

def open_directory():
    selected_directory = folder_tree.item(folder_tree.selection())["text"]
    if selected_directory == "..":
        current_dir = os.path.dirname(current_directory.get())
        current_directory.set(current_dir)
    else:
        current_directory.set(os.path.join(current_directory.get(), selected_directory))
    refresh_list()

def play_selected_video():
    selected_item = file_tree.item(file_tree.selection())["text"]
    if selected_item.lower().endswith(".mp4"):
        file_path = os.path.join(current_directory.get(), selected_item)
        play_video(file_path)

def refresh_list():
    current_dir = current_directory.get()
    folders, mp4_files = list_files_and_folders(current_dir)

    folder_tree.delete(*folder_tree.get_children())
    folder_tree.insert("", "end", text="..")
    for folder in folders:
        folder_tree.insert("", "end", text=folder)

    file_tree.delete(*file_tree.get_children())
    for mp4_file in mp4_files:
        file_tree.insert("", "end", text=mp4_file)

app = tk.Tk()
app.title("File Explorer")

current_directory = tk.StringVar()
current_directory.set(os.getcwd())

frame = ttk.Frame(app)
frame.pack(padx=10, pady=10)

folder_tree = ttk.Treeview(frame)
folder_tree.heading("#0", text="Folders")
folder_tree.pack(side="left")

file_tree = ttk.Treeview(frame)
file_tree.heading("#0", text=".mp4 Files")
file_tree.pack(side="right")

folder_tree.bind("<Double-1>", lambda event: open_directory())
file_tree.bind("<Double-1>", lambda event: play_selected_video())

refresh_button = ttk.Button(app, text="Refresh", command=refresh_list)
refresh_button.pack()

combine_button = ttk.Button(app, text="Combine All", command=lambda: combine_and_delete_mp4_files(current_directory.get()))
combine_button.pack()

app.mainloop()