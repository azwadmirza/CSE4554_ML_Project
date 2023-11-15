def __virtual__():
    # Ensure that daemontools is installed properly.
    BINS = frozenset(('svc', 'supervise', 'svok'))
    return __virtualname__ if all(salt.utils.which(b) for b in BINS) else False