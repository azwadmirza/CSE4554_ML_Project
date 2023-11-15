def main(ctx, verbose, broadcast_support):
    if verbose:
        global log
        import logging
        format = ('%(asctime)-15s %(threadName)-15s '
                  '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
        log = logging.getLogger('pymodbus')
        logging.basicConfig(format=format)
        log.setLevel(logging.DEBUG)
    ctx.obj = {"broadcast": broadcast_support}