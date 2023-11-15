def resolveEntryPoint(entryPoint):
    """
    Returns the path to the given entry point (see setup.py) that *should* work on a worker. The
    return value may be an absolute or a relative path.
    """
    if hasattr(sys, 'real_prefix'):
        # Inside a virtualenv we will use absolute paths to the entrypoints. For clusters this
        # means that if Toil is installed in a virtualenv on the leader, it must be installed in
        # a virtualenv located at the same path on the worker.
        path = os.path.join(os.path.dirname(sys.executable), entryPoint)
        assert os.path.isfile(path)
        assert os.access(path, os.X_OK)
        return path
    else:
        # Outside a virtualenv it is hard to predict where the entry points got installed. It is
        # the reponsibility of the user to ensure that they are present on PATH and point to the
        # correct version of Toil. This is still better than an absolute path because it gives
        # the user control over Toil's location on both leader and workers.
        return entryPoint