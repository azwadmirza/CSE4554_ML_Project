def version_tnf(t1, t2=None):
    # type: (Any, Any) -> Any
    """
    return True if ruamel.yaml version_info < t1, None if t2 is specified and bigger else False
    """
    from dynaconf.vendor.ruamel.yaml import version_info  # NOQA

    if version_info < t1:
        return True
    if t2 is not None and version_info < t2:
        return None
    return False