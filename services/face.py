"""Face detection helpers with optional MTCNN (facenet-pytorch) and OpenCV fallback.

This module avoids hard-failing at import time when OpenCV isn't installed by
detecting availability and using safe fallbacks (Pillow-based resize) so the
application can start in lightweight environments.
"""
import logging
import numpy as np

try:
    from facenet_pytorch import MTCNN
    MTCNN_AVAILABLE = True
except Exception:
    MTCNN_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def detect_faces_in_frame(frame, mtcnn=None, min_size=40):
    """Return list of bounding boxes [x1,y1,x2,y2] for faces in an RGB frame.

    If neither MTCNN nor OpenCV are available, returns an empty list.
    """
    boxes = []
    if MTCNN_AVAILABLE and mtcnn is not None:
        try:
            results = mtcnn.detect(frame)
            if results is not None:
                b, _ = results
                if b is not None:
                    for box in b:
                        x1, y1, x2, y2 = map(int, box.tolist())
                        if (x2 - x1) >= min_size and (y2 - y1) >= min_size:
                            boxes.append([x1, y1, x2, y2])
        except Exception:
            boxes = []

    if not boxes and CV2_AVAILABLE:
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            rects = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_size, min_size))
            for (x, y, w, h) in rects:
                boxes.append([int(x), int(y), int(x + w), int(y + h)])
        except Exception:
            boxes = []

    if not boxes and not CV2_AVAILABLE and not MTCNN_AVAILABLE:
        logging.debug('No face detector available (cv2 and MTCNN unavailable).')

    return boxes


def crop_face(frame, box, size=(224,224)):
    x1, y1, x2, y2 = box
    h, w = frame.shape[:2]
    x1 = max(0, x1); y1 = max(0, y1); x2 = min(w, x2); y2 = min(h, y2)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    # Prefer OpenCV resize if available
    if CV2_AVAILABLE:
        try:
            return cv2.resize(crop, size)
        except Exception:
            pass
    # Fallback to Pillow-based resize if available
    if PIL_AVAILABLE:
        try:
            im = Image.fromarray(crop)
            im = im.resize(size, resample=Image.BILINEAR)
            return np.asarray(im)
        except Exception:
            return None
    # Last-resort: attempt a very simple nearest-neighbor numpy resize (low quality)
    try:
        return np.array(Image.fromarray(crop).resize(size)) if PIL_AVAILABLE else None
    except Exception:
        return None
