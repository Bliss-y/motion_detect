import cv2
import numpy as np
import datetime
import os
import subprocess as sp


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")

def background_subtraction(f1, f2, shapeErode, shapeOpen):
    subtraction = (np.float32(f1) - np.float32(f2))**2
    if len(f1.shape) == 3:
        subtraction = np.sum(subtraction, axis=2);
    st1 = cv2.getStructuringElement(cv2.MORPH_RECT, shapeErode);
    subtraction = cv2.morphologyEx(subtraction, cv2.MORPH_ERODE, st1)
    l, threshar = cv2.threshold(subtraction, 200, 255, cv2.THRESH_BINARY)
    st2 = cv2.getStructuringElement(cv2.MORPH_RECT, shapeOpen)
    threshar = cv2.morphologyEx(np.float32(threshar), cv2.MORPH_OPEN,st2)
    return threshar;


def save_video(frames, folder, dimensions,compress=False):
    outer = f"{folder}/{str(datetime.datetime.now().date())}";
    print(outer);
    create_directory_if_not_exists(outer)
    vid = str(datetime.datetime.now().timestamp());
    name = f"{outer}/{vid}.mp4";
    cursor = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"mp4v"), 10, dimensions);
    for i in frames:
        cursor.write(i); 
    cursor.release();
    if compress:
        output = os.path.join(f"{folder}/compressed/{vid}.mp4")
        process = ["ffmpeg", "-i", name, "-c:v", "libx264", "-crf", "23", "-c:a", "aac", "-strict", "experimental",output]
        sp.run(process)
    return name;

def detect_cap(cap, thread_element):
    mots = [];
    allFrames = [];
    last_detected = 0
    lastf = 0;
    frame_num = 0;
    while True:
        ret, frame = cap.read();
        if not ret:
            if len(mots) > 10:
                save_video(mots, "./motions",(lastf.shape[1], lastf.shape[0]));
            if len(allFrames) > 10:
                save_video(allFrames, "./fullCaptures", (lastf.shape[1], lastf.shape[0]), compress=True)
            last_detected = 0
            mots = [];
            break;
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);
        frame_num+=1
        frameshape=(frame.shape[1], frame.shape[0]);
        if frame_num == 1:
            lastf = np.copy(gray)
            continue;
        if frame_num == 30:
            frame_num = 1;
            save_video(allFrames, "./fullCaptures",frameshape, True); 
            allFrames = [];
        allFrames.append(frame); 
        if len(mots) >= 30:
            save_video(mots,"./motions", frameshape)
            frame_since_last_motion = 0
            mots = [];
        fm = background_subtraction(lastf, gray, (15,15), (2,2));
        lastf = np.copy(gray)
        if last_detected >= 10:
            if len(mots) > 10:
                save_video(mots, "./motions",frameshape)
            mots = [];
        #at least 5 pixels should be moving
        if fm.sum() < 255*5:
            thread_element.put(frame); 
            last_detected +=1;
            continue
        
        contours, _ = cv2.findContours(fm.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        box = (0,0,0,0);
        curr_area = 0;
        #only save the biggest box;
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w+h > curr_area:
                curr_area = w+h; 
                box = (x, y, x + w, y + h)
        x1, y1, x2, y2 = box;
        
        cv2.rectangle(frame, (x1, y1), (x2, y2 ), (0, 255, 0), 2)
        mots.append(frame)
        thread_element.put(frame);
        last_detected = 0;
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release();
    cv2.destroyAllWindows();
    