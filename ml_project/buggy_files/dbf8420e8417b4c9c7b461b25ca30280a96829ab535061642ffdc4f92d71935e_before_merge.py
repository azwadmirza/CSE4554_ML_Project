def info(vac: miio.Vacuum):
    """Return device information."""
    res = vac.info()

    click.echo("%s" % res)
    _LOGGER.debug("Full response: %s", pf(res.raw))