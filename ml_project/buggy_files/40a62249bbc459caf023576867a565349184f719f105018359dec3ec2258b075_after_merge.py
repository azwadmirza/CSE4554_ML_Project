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
        xml_doc = XMLParser(filename)
    except:
        return False
    # check if node "*/eventParameters/event" for the global namespace exists
    try:
        namespace = xml_doc._getFirstChildNamespace()
        xml_doc.xpath('eventParameters', namespace=namespace)[0]
    except:
        return False
    return True