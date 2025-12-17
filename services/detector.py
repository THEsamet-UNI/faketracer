import os
import numpy as np
from .video import extract_frames
from .face import detect_faces_in_frame, crop_face

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


class MockDetector:
    """A lightweight placeholder detector.
    Computes a simple per-frame artifact score using Laplacian variance
    (proxy for blurriness / processing artifacts). This is NOT a real
    deepfake classifier — it's a scaffold until a trained model is added.
    """
    def __init__(self):
        pass

    def predict_frame(self, frame):
        # frame: HxWx3 RGB numpy array
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        lv = cv2.Laplacian(gray, cv2.CV_64F).var()
        # normalize into 0-1 range heuristically
        score = 1.0 - (1.0 / (1.0 + lv / 100.0))
        # convert to 0-100
        return float(max(0.0, min(100.0, score * 100)))


class Detector:
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None
        if model_path and TORCH_AVAILABLE:
            self._load_model(model_path)
        else:
            self.model = MockDetector()

    def _load_model(self, path):
        try:
            # Placeholder: user should replace with actual model loading
            self.model = torch.load(path, map_location='cpu')
        except Exception as e:
            print('Could not load detector model:', e)
            self.model = MockDetector()

    def predict_frames(self, frames):
        """Return list of per-frame scores (0-100)."""
        scores = []
        for f in frames:
            try:
                # attempt to crop face first (prefer largest face)
                face_boxes = detect_faces_in_frame(f)
                if face_boxes:
                    # pick largest box
                    face_boxes.sort(key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
                    crop = crop_face(f, face_boxes[0])
                    if crop is not None:
                        input_img = crop
                    else:
                        input_img = f
                else:
                    input_img = f

                if TORCH_AVAILABLE and hasattr(self.model, 'eval') and not isinstance(self.model, MockDetector):
                    # User-provided model expected to accept tensors
                    import torch
                    img = torch.from_numpy(input_img.astype('float32') / 255.0).permute(2,0,1).unsqueeze(0)
                    with torch.no_grad():
                        out = self.model(img)
                    # Expect output in [0,1] fake probability
                    if isinstance(out, (list, tuple)):
                        out = out[0]
                    val = float(out.squeeze().item())
                    scores.append(max(0.0, min(100.0, val * 100.0)))
                else:
                    scores.append(self.model.predict_frame(input_img))
            except Exception:
                scores.append(self.model.predict_frame(f))
        return scores

    def detect_video(self, video_path, max_frames=64):
        frames = extract_frames(video_path, max_frames=max_frames)
        if not frames:
            return {'error':'no_frames', 'frames':[]}
        scores = self.predict_frames(frames)
        avg = float(np.mean(scores)) if scores else 0.0
        # heuristic thresholding: avg > 60 => likely fake (this is arbitrary)
        label = 'unknown'
        if avg >= 65:
            label = 'likely_fake'
        elif avg <= 35:
            label = 'likely_real'
        return {
            'label': label,
            'average_score': avg,
            'frame_count': len(scores),
            'frame_scores': scores
        }


def get_detector(model_path=None):
    return Detector(model_path=model_path)
