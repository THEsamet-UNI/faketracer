import os
import requests

URL = 'https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_5mb.mp4'
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
OUT_PATH = os.path.join(OUT_DIR, 'sample_video.mp4')

os.makedirs(OUT_DIR, exist_ok=True)
print('Downloading', URL)
try:
    r = requests.get(URL, stream=True, timeout=30)
    r.raise_for_status()
    with open(OUT_PATH, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print('Saved to', OUT_PATH)
except Exception as e:
    print('Download failed:', e)
    raise
