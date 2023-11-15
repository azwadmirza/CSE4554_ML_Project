    def check_parent(pid, lvl=0):
        ppid = processes[pid].get('parent_pid')
        if ppid and processes[ppid]['executable'].lower().rsplit('.', 1)[0] in SHELL_NAMES:
            return processes[ppid]['executable']
        if lvl >= max_depth:
            return
        return check_parent(ppid, lvl=lvl+1)