def brian_object_exception(message, brianobj, original_exception):
    '''
    Returns a `BrianObjectException` derived from the original exception.

    Creates a new class derived from the class of the original exception
    and `BrianObjectException`. This allows exception handling code to
    respond both to the original exception class and `BrianObjectException`.

    See `BrianObjectException` for arguments and notes.
    '''
    DerivedBrianObjectException = type('BrianObjectException',
                                       (BrianObjectException, original_exception.__class__),
                                       {})
    new_exception = DerivedBrianObjectException(message, brianobj, original_exception)
    # Copy over all exception attributes
    for attribute in dir(original_exception):
        if attribute.startswith('_'):
            continue
        setattr(new_exception, attribute, getattr(original_exception, attribute))
    return new_exception