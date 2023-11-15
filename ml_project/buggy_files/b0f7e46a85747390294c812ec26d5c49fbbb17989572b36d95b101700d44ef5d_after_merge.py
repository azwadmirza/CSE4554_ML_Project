def tag_to_version(tag):
    """
    take a tag that might be prefixed with a keyword and return only the version part
    """
    trace("tag", tag)
    if "+" in tag:
        warnings.warn("tag %r will be stripped of the local component" % tag)
        tag = tag.split("+")[0]
    # lstrip the v because of py2/py3 differences in setuptools
    # also required for old versions of setuptools
    prefix_match = TAG_PREFIX.match(tag)
    if prefix_match is not None:
        version = prefix_match.group(1)
    else:
        version = tag
    trace("version pre parse", version)
    if VERSION_CLASS is None:
        return version
    version = pkg_parse_version(version)
    trace("version", repr(version))
    if isinstance(version, VERSION_CLASS):
        return version