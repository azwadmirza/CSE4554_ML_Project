def abstract(cls):
    ''' A decorator to mark abstract base classes derived from |HasProps|.

    '''
    if not issubclass(cls, HasProps):
        raise TypeError("%s is not a subclass of HasProps" % cls.__name__)

    cls.__doc__ += _ABSTRACT_ADMONITION

    return cls