import os
import sys

# Ensure root directory is on the path so that app, config, routes, etc. import cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel entrypoint
# The 'app' object is the WSGI callable
