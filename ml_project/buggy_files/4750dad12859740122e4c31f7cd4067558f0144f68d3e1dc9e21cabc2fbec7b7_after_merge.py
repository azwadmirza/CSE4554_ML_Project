    def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                       timeout=None, on_terminate=None):
        """
        Kill a process tree (including grandchildren) with sig and return a
        (gone, still_alive) tuple.

        "on_terminate", if specified, is a callabck function which is called
        as soon as a child terminates.

        This is an new method not present in QtKernelManager.
        """
        assert pid != os.getpid()  # Won't kill myself!

        # This is necessary to avoid showing an error when restarting the
        # kernel after it failed to start in the first place.
        # Fixes spyder-ide/spyder#11872
        try:
            parent = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return ([], [])

        children = parent.children(recursive=True)

        if include_parent:
            children.append(parent)

        for child_process in children:
            # This is necessary to avoid an error when restarting the
            # kernel that started a PyQt5 application in the background.
            # Fixes spyder-ide/spyder#13999
            try:
                child_process.send_signal(sig)
            except psutil.AccessDenied:
                return ([], [])

        gone, alive = psutil.wait_procs(
            children,
            timeout=timeout,
            callback=on_terminate,
        )

        return (gone, alive)