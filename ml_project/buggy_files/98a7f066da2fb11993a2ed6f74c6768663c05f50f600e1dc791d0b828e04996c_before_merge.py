def get_pip():
    """Returns a lazily instantiated global Pip object that is safe for un-coordinated use."""
    global _PIP
    if _PIP is None:
        _PIP = Pip.create(path=os.path.join(ENV.PEX_ROOT, "pip.pex"))
    return _PIP