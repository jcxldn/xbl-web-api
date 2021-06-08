from flask_caching import Cache

import time
import base64

default_secs = 300

cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp'})

def add_cache_headers(res):
    print("Adding cache headers...")
    # ----------
    # Create a X-Queried-At header
    # ----------
    # 1. Get the epoch
    epoch = time.time()
    # 2. Convert it to ASCII bytes (?)
    epoch_str_bytes = str(epoch).encode("ascii")
    # 3. Base64 encode the bytes
    epoch_b64 = base64.b64encode(epoch_str_bytes)
    res.headers["X-Queried-At"] = epoch_b64
    return res