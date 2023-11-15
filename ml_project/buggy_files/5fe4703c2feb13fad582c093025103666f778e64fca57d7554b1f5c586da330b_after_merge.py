            def __init__(self_, *args, **kwds):
                # don't call sys.exit() on IOErrors
                kwds['handle_io_errors'] = False
                kwds['error_handler'] = 'sphinx'  # py3: handle error on open.
                FileInput.__init__(self_, *args, **kwds)