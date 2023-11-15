def __virtual__():
    # Ensure that daemontools is installed properly.
    BINS = frozenset(('svc', 'supervise', 'svok'))
    if all(salt.utils.which(b) for b in BINS) and SERVICE_DIR:
        return __virtualname__
    return False