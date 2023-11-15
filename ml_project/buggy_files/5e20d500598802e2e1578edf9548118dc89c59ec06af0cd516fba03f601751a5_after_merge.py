def distVersion():
    """
    The distribution version identifying a published release on PyPI.
    """
    from pkg_resources import parse_version
    build_number = buildNumber()
    parsedBaseVersion = parse_version(baseVersion)
    if isinstance(parsedBaseVersion, tuple):
        raise RuntimeError("Setuptools version 8.0 or newer required. Update by running "
                           "'pip install setuptools --upgrade'")

    if build_number is not None and parsedBaseVersion.is_prerelease:
        return baseVersion + '.dev' + build_number
    else:
        return baseVersion