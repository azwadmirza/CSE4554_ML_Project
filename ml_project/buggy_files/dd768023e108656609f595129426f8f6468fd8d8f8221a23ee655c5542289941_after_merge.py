def pid_exists(pid):
    """Check for the existence of a unix PID."""
    if not _psposix.pid_exists(pid):
        return False
    else:
        # Linux's apparently does not distinguish between PIDs and TIDs
        # (thread IDs).
        # listdir("/proc") won't show any TID (only PIDs) but
        # os.stat("/proc/{tid}") will succeed if {tid} exists.
        # os.kill() can also be passed a TID. This is quite confusing.
        # In here we want to enforce this distinction and support PIDs
        # only, see:
        # https://github.com/giampaolo/psutil/issues/687
        try:
            # Note: already checked that this is faster than using a
            # regular expr. Also (a lot) faster than doing
            # 'return pid in pids()'
            with open_binary("%s/%s/status" % (get_procfs_path(), pid)) as f:
                for line in f:
                    if line.startswith(b"Tgid:"):
                        tgid = int(line.split()[1])
                        # If tgid and pid are the same then we're
                        # dealing with a process PID.
                        return tgid == pid
                raise ValueError("'Tgid' line not found")
        except (EnvironmentError, ValueError):
            return pid in pids()