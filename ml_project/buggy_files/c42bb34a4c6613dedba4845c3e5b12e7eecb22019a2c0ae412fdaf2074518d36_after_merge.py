def return_values(obj):
    """ Return stringified values from datastructures. For use with removing
    sensitive values pre-jsonification."""
    if isinstance(obj, basestring):
        if obj:
            if isinstance(obj, bytes):
                yield obj
            else:
                # Unicode objects should all convert to utf-8
                # (still must deal with surrogateescape on python3)
                yield obj.encode('utf-8')
        return
    elif isinstance(obj, Sequence):
        for element in obj:
            for subelement in return_values(element):
                yield subelement
    elif isinstance(obj, Mapping):
        for element in obj.items():
            for subelement in return_values(element[1]):
                yield subelement
    elif isinstance(obj, (bool, NoneType)):
        # This must come before int because bools are also ints
        return
    elif isinstance(obj, NUMBERTYPES):
        yield str(obj)
    else:
        raise TypeError('Unknown parameter type: %s, %s' % (type(obj), obj))