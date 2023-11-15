def new_error_context(fmt_, *args, **kwargs):
    """
    A contextmanager that prepend contextual information to any exception
    raised within.  If the exception type is not an instance of NumbaError,
    it will be wrapped into a InternalError.   The exception class can be
    changed by providing a "errcls_" keyword argument with the exception
    constructor.

    The first argument is a message that describes the context.  It can be a
    format string.  If there are additional arguments, it will be used as
    ``fmt_.format(*args, **kwargs)`` to produce the final message string.
    """
    errcls = kwargs.pop('errcls_', InternalError)

    loc = kwargs.get('loc', None)
    if loc is not None and not loc.filename.startswith(_numba_path):
        loc_info.update(kwargs)

    try:
        yield
    except NumbaError as e:
        e.add_context(_format_msg(fmt_, args, kwargs))
        raise
    except Exception as e:
        newerr = errcls(e).add_context(_format_msg(fmt_, args, kwargs))
        six.reraise(type(newerr), newerr, sys.exc_info()[2])