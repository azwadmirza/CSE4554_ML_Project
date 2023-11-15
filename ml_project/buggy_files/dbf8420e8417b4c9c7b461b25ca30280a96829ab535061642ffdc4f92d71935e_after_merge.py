def info(vac: miio.Vacuum):
    """Return device information."""
    try:
        res = vac.info()

        click.echo("%s" % res)
        _LOGGER.debug("Full response: %s", pf(res.raw))
    except TypeError:
        click.echo("Unable to fetch info, this can happen when the vacuum "
                   "is not connected to the Xiaomi cloud.")