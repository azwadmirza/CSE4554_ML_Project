    def pid_running(pid):
        """Return True if we know if process with pid is currently running,
        False if it isn't running, and None if we don't know for sure."""
        if os.name == 'nt':
            import win32api
            import win32con
            import pywintypes
            process = None
            try:
                process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0,
                                               pid)
            except pywintypes.error as error:
                if error.winerror == 87:
                    # parameter incorrect, PID does not exist
                    return False
                elif error.winerror == 5:
                    # access denied, means nevertheless PID still exists
                    return True
                else:
                    msg = "Warning: unable to check if PID %d still running"
                    log.Log(msg % pid, 2)
                    return None  # we don't know if the process is running
            else:
                if process:
                    win32api.CloseHandle(process)
                    return True
                else:
                    return False
        else:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:  # errno.ESRCH - pid doesn't exist
                return False
            except OSError:  # any other OS error
                log.Log(
                    "Warning: unable to check if PID %d still running" % (pid, ),
                    2)
                return None  # we don't know if the process is still running
            else:  # the process still exists
                return True