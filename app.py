import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask_utils import configure_frozen_path
configure_frozen_path()

backend_dir = os.path.join(project_root, 'backend')
os.chdir(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import start_app

if __name__ == '__main__':
    start_app()
