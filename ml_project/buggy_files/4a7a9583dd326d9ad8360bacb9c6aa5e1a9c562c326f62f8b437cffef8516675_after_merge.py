def resolveEntryPoint(entryPoint):
    """
    Returns the path to the given entry point (see setup.py) that *should* work on a worker. The
    return value may be an absolute or a relative path.
    """
    if hasattr(sys, 'real_prefix'):
        path = os.path.join(os.path.dirname(sys.executable), entryPoint)
        # Inside a virtualenv we try to use absolute paths to the entrypoints. 
        if os.path.isfile(path):
            # If the entrypoint is present, Toil must have been installed into the virtualenv (as 
            # opposed to being included via --system-site-packages). For clusters this means that 
            # if Toil is installed in a virtualenv on the leader, it must be installed in
            # a virtualenv located at the same path on each worker as well.
            assert os.access(path, os.X_OK)
            return path
        else:
            # For virtualenv's that have the toil package directory on their sys.path but whose 
            # bin directory lacks the Toil entrypoints, i.e. where Toil is included via 
            # --system-site-packages, we rely on PATH just as if we weren't in a virtualenv. 
            return entryPoint
    else:
        # Outside a virtualenv it is hard to predict where the entry points got installed. It is
        # the reponsibility of the user to ensure that they are present on PATH and point to the
        # correct version of Toil. This is still better than an absolute path because it gives
        # the user control over Toil's location on both leader and workers.
        return entryPoint