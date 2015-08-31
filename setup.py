import cx_Freeze
import sys
import requests.certs

base = "Win32GUI"

executables = [cx_Freeze.Executable("Soundcloud App.py", base = base, icon = "unnamed.ico")]

cx_Freeze.setup(
    name ="SoundcloudApp",
    options = {"build_exe":{"packages":["tkinter","soundcloud"], "include_files":["cacert.pem","ok.png", "cross.png", "loupe.png"] }},
    executables = executables
    )
