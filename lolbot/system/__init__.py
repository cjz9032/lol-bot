import sys

if sys.platform == "darwin":  # macOS
    from .macos import mouse, keys, window, cmd
    RESOLUTION = (584, 383)
    OS = 'macOS'
elif sys.platform == "win32":  # Windows
    from .windows import mouse, keys, window, cmd
    version_info = sys.getwindowsversion()
    if version_info.major == 10 and version_info.build >= 22000: # Win11
        RESOLUTION = (606, 440)
    else: # Win10
        RESOLUTION = (600, 420)
    OS = 'Windows'
else:
    raise ImportError("Unsupported operating system")
