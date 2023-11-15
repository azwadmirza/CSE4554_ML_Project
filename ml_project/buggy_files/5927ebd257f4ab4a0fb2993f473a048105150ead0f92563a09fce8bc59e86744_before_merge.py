def kill_process_tree(pid, include_parent=True):
    try:
        import psutil
    except ImportError:  # pragma: no cover
        return
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    plasma_sock_dir = None
    children = proc.children(recursive=True)
    if include_parent:
        children.append(proc)
    for p in children:
        try:
            if 'plasma' in p.name():
                plasma_sock_dir = next((conn.laddr for conn in p.connections('unix')
                                        if 'plasma' in conn.laddr), None)
            p.kill()
        except psutil.NoSuchProcess:  # pragma: no cover
            pass
    if plasma_sock_dir:
        shutil.rmtree(plasma_sock_dir, ignore_errors=True)