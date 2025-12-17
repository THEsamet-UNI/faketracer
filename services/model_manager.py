import os
import hashlib
import requests

def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()

def download_model(url, dest_path, expected_sha256=None, timeout=30):
    """Download a file from `url` to `dest_path`. Optionally verify sha256.
    Returns (True, message) on success or (False, error_message) on failure.
    """
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        return False, f'download_failed: {e}'
    if expected_sha256:
        try:
            got = sha256_of_file(dest_path)
            if got.lower() != expected_sha256.lower():
                return False, f'sha_mismatch: expected {expected_sha256}, got {got}'
        except Exception as e:
            return False, f'sha_check_failed: {e}'
    return True, 'ok'

def load_torch_model(path, map_location='cpu'):
    try:
        import torch
        model = torch.load(path, map_location=map_location)
        return True, model
    except Exception as e:
        return False, str(e)
