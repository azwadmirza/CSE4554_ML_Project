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
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        if include_parent:
            children.append(parent)

        for child_process in children:
            child_process.send_signal(sig)

        gone, alive = psutil.wait_procs(
            children,
            timeout=timeout,
            callback=on_terminate,
        )

        return (gone, alive)