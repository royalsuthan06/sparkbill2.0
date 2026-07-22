import os
import sys

# Change working directory to backend folder so relative paths resolved correctly
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import start_app

if __name__ == '__main__':
    start_app()
