def check_libcloud_version(reqver=LIBCLOUD_MINIMAL_VERSION, why=None):
    """
    Compare different libcloud versions
    """
    if not HAS_LIBCLOUD:
        return False

    if not isinstance(reqver, (list, tuple)):
        raise RuntimeError(
            "'reqver' needs to passed as a tuple or list, i.e., (0, 14, 0)"
        )
    try:
        import libcloud  # pylint: disable=redefined-outer-name
    except ImportError:
        raise ImportError(
            "salt-cloud requires >= libcloud {} which is not installed".format(
                ".".join([str(num) for num in reqver])
            )
        )

    if LIBCLOUD_VERSION_INFO >= reqver:
        return libcloud.__version__

    errormsg = "Your version of libcloud is {}. ".format(libcloud.__version__)
    errormsg += "salt-cloud requires >= libcloud {}".format(
        ".".join([str(num) for num in reqver])
    )
    if why:
        errormsg += " for {}".format(why)
    errormsg += ". Please upgrade."
    raise ImportError(errormsg)