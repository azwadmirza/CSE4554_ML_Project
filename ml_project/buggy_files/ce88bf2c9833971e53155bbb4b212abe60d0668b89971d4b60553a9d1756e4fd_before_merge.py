def getdoc(obj):
    """Stable wrapper around inspect.getdoc.

    This can't crash because of attribute problems.

    It also attempts to call a getdoc() method on the given object.  This
    allows objects which provide their docstrings via non-standard mechanisms
    (like Pyro proxies) to still be inspected by ipython's ? system."""
    # Allow objects to offer customized documentation via a getdoc method:
    try:
        ds = obj.getdoc()
    except Exception:
        pass
    else:
        # if we get extra info, we add it to the normal docstring.
        if isinstance(ds, basestring):
            return inspect.cleandoc(ds)
    
    try:
        return inspect.getdoc(obj)
    except Exception:
        # Harden against an inspect failure, which can occur with
        # SWIG-wrapped extensions.
        return None