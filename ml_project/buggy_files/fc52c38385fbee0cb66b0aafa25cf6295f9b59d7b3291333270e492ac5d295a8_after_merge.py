def disk_usage(path):
    if platform.system() == 'Windows':
        import sys
        _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
        if sys.version_info >= (3,) or isinstance(path, unicode):
            method = ctypes.windll.kernel32.GetDiskFreeSpaceExW
        else:
            method = ctypes.windll.kernel32.GetDiskFreeSpaceExA
        ret = method(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
        if ret == 0:
            logger.log("Unable to determine free space, something went wrong", logger.WARNING)
            raise ctypes.WinError()
        return free.value

    elif hasattr(os, 'statvfs'):  # POSIX
        import subprocess
        call = subprocess.Popen(["df", "-B", "K", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = call.communicate()[0]
        return int(output.split("\n")[1].split()[3]) * 1024
    else:
        raise Exception("Unable to determine free space on your OS")