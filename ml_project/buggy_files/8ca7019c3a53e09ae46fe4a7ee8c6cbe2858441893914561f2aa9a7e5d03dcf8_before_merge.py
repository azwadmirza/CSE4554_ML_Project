def check_package_data(dist, attr, value):
    """Verify that value is a dictionary of package names to glob lists"""
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                break
            try:
                iter(v)
            except TypeError:
                break
        else:
            return
    raise DistutilsSetupError(
        attr + " must be a dictionary mapping package names to lists of "
        "wildcard patterns"
    )