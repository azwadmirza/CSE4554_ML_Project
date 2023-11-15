def require_pkgresources(name):
    try:
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          import pkg_resources  # vendor:skip
        else:
          import pex.third_party.pkg_resources as pkg_resources
  # noqa: F401
    except ImportError:
        raise RuntimeError("'{0}' needs pkg_resources (part of setuptools).".format(name))