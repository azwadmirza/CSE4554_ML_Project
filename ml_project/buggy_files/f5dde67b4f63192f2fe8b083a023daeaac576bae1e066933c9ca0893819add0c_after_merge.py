def abstract(cls):
    ''' A decorator to mark abstract base classes derived from |HasProps|.

    '''
    if not issubclass(cls, HasProps):
        raise TypeError("%s is not a subclass of HasProps" % cls.__name__)

    # running python with -OO will discard docstrings -> __doc__ is None
    if cls.__doc__ is not None:
        cls.__doc__ += _ABSTRACT_ADMONITION

    return cls