def ismock(subject: Any) -> bool:
    """Check if the object is mocked."""
    # check the object has '__sphinx_mock__' attribute
    if not hasattr(subject, '__sphinx_mock__'):
        return False

    # check the object is mocked module
    if isinstance(subject, _MockModule):
        return True

    try:
        # check the object is mocked object
        __mro__ = safe_getattr(type(subject), '__mro__', [])
        if len(__mro__) > 2 and __mro__[1] is _MockObject:
            return True
    except AttributeError:
        pass

    return False