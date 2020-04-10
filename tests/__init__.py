from pathlib import Path
import subprocess

root_path = str(Path(__file__).parent)
# This opens an http server on the background
subprocess.Popen(["python3", "-m", "http.server", root_path])
