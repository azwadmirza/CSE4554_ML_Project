            def __init__(self_, *args, **kwds):
                # don't call sys.exit() on IOErrors
                kwds['handle_io_errors'] = False
                FileInput.__init__(self_, *args, **kwds)