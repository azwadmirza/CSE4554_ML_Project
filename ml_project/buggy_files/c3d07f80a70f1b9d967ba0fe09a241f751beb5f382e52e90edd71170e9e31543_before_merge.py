def parse_version(version):
    """Use parse_version from pkg_resources or distutils as available."""
    global parse_version
    try:
        from pex.third_party.pkg_resources import parse_version
    except ImportError:
        from distutils.version import LooseVersion as parse_version
    return parse_version(version)