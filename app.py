import os
import sys

# Locate and configure Python DLL for pythonnet/clr_loader in frozen environments
if getattr(sys, 'frozen', False):
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
            # Add to PATH so that clr_loader/Windows can find python3xx.dll and other dependency DLLs
            if d not in os.environ['PATH']:
                os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
            
            for file in os.listdir(d):
                if file.lower().startswith('python3') and file.lower().endswith('.dll'):
                    py_dll = os.path.abspath(os.path.join(d, file))
                    break
    if py_dll:
        os.environ['PYTHONNET_PYDLL'] = py_dll

# Change working directory to backend folder so relative paths resolved correctly
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import start_app

if __name__ == '__main__':
    start_app()
