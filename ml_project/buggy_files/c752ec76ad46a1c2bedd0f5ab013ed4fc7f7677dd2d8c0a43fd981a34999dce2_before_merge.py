def drange(v0, v1, d):
    """Returns a discrete range."""
    assert v0 < v1, str((v0, v1, d))
    return range(int(v0)//d, int(v1+d)//d)