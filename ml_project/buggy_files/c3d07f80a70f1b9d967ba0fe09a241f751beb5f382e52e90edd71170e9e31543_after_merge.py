def parse_version(version):
    """Use parse_version from pkg_resources or distutils as available."""
    global parse_version
    try:
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from pkg_resources import parse_version  # vendor:skip
        else:
          from pex.third_party.pkg_resources import parse_version

    except ImportError:
        from distutils.version import LooseVersion as parse_version
    return parse_version(version)