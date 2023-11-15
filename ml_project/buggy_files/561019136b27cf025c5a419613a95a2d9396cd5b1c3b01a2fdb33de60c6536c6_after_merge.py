def votable_handler(xml_table):
    """
    Returns a VOtable object from a VOtable style xml string

    In order to get a VOtable object, it has to be parsed from an xml file or
    file-like object. This function creates a file-like object via the
    StringIO module, writes the xml data to it, then passes the file-like
    object to parse_single_table() from the astropy.io.votable.table module
    and thereby creates a VOtable object.

    Parameters
    ----------
    xml_table : str
        Contains the VOtable style xml data

    Returns
    -------
    votable : `astropy.io.votable.tree.Table`
        A properly formatted VOtable object

    Examples
    --------
    >>> from sunpy.net.helio import hec
    >>> temp = hec.suds_unwrapper(xml_string)
    >>> type(temp)
    unicode
    >>> temp = hec.votable_handler(temp)
    >>> type(temp)
    astropy.io.votable.tree.Table
    """
    fake_file = six.BytesIO()
    fake_file.write(six.b(xml_table))
    votable = parse_single_table(fake_file)
    fake_file.close()
    return votable