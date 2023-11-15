def get_shell(pid=None, max_depth=4):
    """Get the shell that the supplied pid or os.getpid() is running in.
    """
    if not pid:
        pid = os.getpid()
    processes = get_all_processes()

    def check_parent(pid, lvl=0):
        ppid = processes[pid].get('parent_pid')
        if ppid and processes[ppid]['executable'].lower().rsplit('.', 1)[0] in SHELL_NAMES:
            return processes[ppid]['executable']
        if lvl >= max_depth:
            return
        return check_parent(ppid, lvl=lvl+1)
    if processes[pid]['executable'].lower().rsplit('.', 1)[0] in SHELL_NAMES:
        return processes[pid]['executable']
    return check_parent(pid)