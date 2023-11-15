def create_input_source(source=None, publicID=None,
                        location=None, file=None, data=None, format=None):
    """
    Return an appropriate InputSource instance for the given
    parameters.
    """

    # test that exactly one of source, location, file, and data is not None.
    if sum((
        source is not None,
        location is not None,
        file is not None,
        data is not None,
    )) != 1:
        raise ValueError(
            'exactly one of source, location, file or data must be given'
        )

    input_source = None

    if source is not None:
        if isinstance(source, InputSource):
            input_source = source
        else:
            if isinstance(source, basestring):
                location = source
            elif hasattr(source, "read") and not isinstance(source, Namespace):
                f = source
                input_source = InputSource()
                input_source.setByteStream(f)
                if f is sys.stdin:
                    input_source.setSystemId("file:///dev/stdin")
                elif hasattr(f, "name"):
                    input_source.setSystemId(f.name)
            else:
                raise Exception("Unexpected type '%s' for source '%s'" %
                                (type(source), source))

    absolute_location = None  # Further to fix for issue 130

    auto_close = False  # make sure we close all file handles we open
    if location is not None:
        # Fix for Windows problem https://github.com/RDFLib/rdflib/issues/145
        if os.path.exists(location):
            location = pathname2url(location)
        base = urljoin("file:", "%s/" % pathname2url(os.getcwd()))
        absolute_location = URIRef(location, base=base).defrag()
        if absolute_location.startswith("file:///"):
            filename = url2pathname(absolute_location.replace("file:///", "/"))
            file = open(filename, "rb")
        else:
            input_source = URLInputSource(absolute_location, format)
        auto_close = True
        # publicID = publicID or absolute_location  # Further to fix
                                                    # for issue 130

    if file is not None:
        input_source = FileInputSource(file)

    if data is not None:
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        input_source = StringInputSource(data)
        auto_close = True

    if input_source is None:
        raise Exception("could not create InputSource")
    else:
        input_source.auto_close |= auto_close
        if publicID is not None:  # Further to fix for issue 130
            input_source.setPublicId(publicID)
        # Further to fix for issue 130
        elif input_source.getPublicId() is None:
            input_source.setPublicId(absolute_location or "")
        return input_source