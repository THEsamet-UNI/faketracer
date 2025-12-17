from services.detector import get_detector
import os

def run_detection(video_path, model_path=None):
    """RQ worker callable: runs detection and returns result dict."""
    detector = get_detector(model_path=model_path)
    return detector.detect_video(video_path)
