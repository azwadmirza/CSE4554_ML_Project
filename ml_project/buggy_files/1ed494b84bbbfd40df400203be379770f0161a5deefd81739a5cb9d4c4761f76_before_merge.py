def check_pids(curmir_incs):
    """Check PIDs in curmir markers to make sure rdiff-backup not running"""
    pid_re = re.compile(r"^PID\s*([0-9]+)", re.I | re.M)

    def extract_pid(curmir_rp):
        """Return process ID from a current mirror marker, if any"""
        match = pid_re.search(curmir_rp.get_string())
        if not match:
            return None
        else:
            return int(match.group(1))

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
                if error[0] == 87:
                    return False
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

    for curmir_rp in curmir_incs:
        assert curmir_rp.conn is Globals.local_connection, (
            "Function must be called locally not over '{conn}'.".format(
                conn=curmir_rp.conn))
        pid = extract_pid(curmir_rp)
        # FIXME differentiate between don't know and know and handle err.errno == errno.EPERM:
        # EPERM clearly means there's a process to deny access to with OSError
        if pid is not None and pid_running(pid):
            log.Log.FatalError(
                """It appears that a previous rdiff-backup session with process
id %d is still running.  If two different rdiff-backup processes write
the same repository simultaneously, data corruption will probably
result.  To proceed with regress anyway, rerun rdiff-backup with the
--force option.""" % (pid, ))