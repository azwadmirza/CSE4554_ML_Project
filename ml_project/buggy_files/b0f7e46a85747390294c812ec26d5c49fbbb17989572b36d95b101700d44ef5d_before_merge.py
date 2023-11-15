def tag_to_version(tag):
    trace("tag", tag)
    if "+" in tag:
        warnings.warn("tag %r will be stripped of the local component" % tag)
        tag = tag.split("+")[0]
    # lstrip the v because of py2/py3 differences in setuptools
    # also required for old versions of setuptools

    version = tag.rsplit("-", 1)[-1].lstrip("v")
    if VERSION_CLASS is None:
        return version
    version = pkg_parse_version(version)
    trace("version", repr(version))
    if isinstance(version, VERSION_CLASS):
        return version