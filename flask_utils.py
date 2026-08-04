import os
import sys


def configure_frozen_path():
    if not getattr(sys, 'frozen', False):
        return

    exe_dir = os.path.dirname(sys.executable)
    search_dirs = [
        os.path.join(exe_dir, '_internal'),
        exe_dir
    ]
    if hasattr(sys, '_MEIPASS'):
        search_dirs.insert(0, os.path.join(sys._MEIPASS, '_internal'))
        search_dirs.insert(0, sys._MEIPASS)

    py_dll = None
    for d in search_dirs:
        if os.path.exists(d):
            if d not in os.environ['PATH']:
                os.environ['PATH'] = d + os.pathsep + os.environ['PATH']

            for file in os.listdir(d):
                if file.lower().startswith('python3') and file.lower().endswith('.dll'):
                    py_dll = os.path.abspath(os.path.join(d, file))
                    break
    if py_dll:
        os.environ['PYTHONNET_PYDLL'] = py_dll
