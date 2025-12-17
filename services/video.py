import os
import cv2

def extract_frames(video_path, max_frames=64, resize=(224,224)):
    """Extract up to `max_frames` frames from video_path as RGB numpy arrays.
    Returns list of frames (BGR->RGB converted if using cv2).
    """
    frames = []
    if not os.path.exists(video_path):
        return frames
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total <= 0:
        # try reading until end
        total = None
    step = 1
    if total and total > max_frames:
        step = max(1, total // max_frames)
    idx = 0
    grabbed = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % step == 0:
            # resize
            if resize:
                frame = cv2.resize(frame, resize)
            # convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            grabbed += 1
            if grabbed >= max_frames:
                break
        idx += 1
    cap.release()
    return frames
