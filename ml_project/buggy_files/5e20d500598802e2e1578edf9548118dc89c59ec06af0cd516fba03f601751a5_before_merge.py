def distVersion():
    """
    The distribution version identifying a published release on PyPI.
    """
    from pkg_resources import parse_version
    build_number = buildNumber()
    if build_number is not None and parse_version(baseVersion).is_prerelease:
        return baseVersion + '.dev' + build_number
    else:
        return baseVersion