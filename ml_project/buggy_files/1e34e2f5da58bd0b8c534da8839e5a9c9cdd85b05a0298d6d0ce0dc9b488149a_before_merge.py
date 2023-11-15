def prepare_context(ctx, config, verbose):
    if ctx.obj is not None:
        return

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ctx.obj = {}
    ctx.obj['conf'] = conf = get_config(config)

    out = StringIO()
    conf.write(out)
    logger.debug('Using config:')
    logger.debug(out.getvalue())

    if conf is None:
        raise click.UsageError('Invalid config file, exiting.')