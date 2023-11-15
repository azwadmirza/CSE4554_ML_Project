def isQuakeML(filename):
    """
    Checks whether a file is QuakeML format.

    :type filename: str
    :param filename: Name of the QuakeML file to be checked.
    :rtype: bool
    :return: ``True`` if QuakeML file.

    .. rubric:: Example

    >>> isQuakeML('/path/to/quakeml.xml')  # doctest: +SKIP
    True
    """
    try:
        p = XMLParser(filename)
    except:
        False
    # check node "*/eventParameters/event" for the global namespace exists
    try:
        namespace = p._getFirstChildNamespace()
        p.xpath('eventParameters', namespace=namespace)[0]
    except:
        return False
    return True