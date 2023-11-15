def isintlike(x):
    """Is x appropriate as an index into a sparse matrix? Returns True
    if it can be cast safely to a machine int.
    """
    if issequence(x):
        return False
    try:
        return bool(int(x) == x)
    except (TypeError, ValueError):
        return False