def check_package_data(dist, attr, value):
    """Verify that value is a dictionary of package names to glob lists"""
    if not isinstance(value, dict):
        raise DistutilsSetupError(
            "{!r} must be a dictionary mapping package names to lists of "
            "string wildcard patterns".format(attr))
    for k, v in value.items():
        if not isinstance(k, six.string_types):
            raise DistutilsSetupError(
                "keys of {!r} dict must be strings (got {!r})"
                .format(attr, k)
            )
        assert_string_list(dist, 'values of {!r} dict'.format(attr), v)