def try_import(objname):
    # type: (unicode) -> Any
    """Import a object or module using *name* and *currentmodule*.
    *name* should be a relative name from *currentmodule* or
    a fully-qualified name.

    Returns imported object or module.  If failed, returns None value.
    """
    try:
        __import__(objname)
        return sys.modules.get(objname)  # type: ignore
    except ImportError:
        modname, attrname = module_sig_re.match(objname).groups()  # type: ignore
        if modname is None:
            return None
        try:
            __import__(modname)
            return getattr(sys.modules.get(modname), attrname, None)
        except ImportError:
            return None