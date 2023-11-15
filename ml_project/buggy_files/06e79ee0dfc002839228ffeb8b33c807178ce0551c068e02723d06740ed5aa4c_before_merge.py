def urlencoded_processor(entity):
    '''
    Accept x-www-form-urlencoded data (run through CherryPy's formatter)
    and reformat it into a Low State data structure.

    Since we can't easily represent complicated data structures with
    key-value pairs, any more complicated requirements (e.g. compound
    commands) must instead be delivered via JSON or YAML.

    For example::

    .. code-block:: bash

        curl -si localhost:8000 -d client=local -d tgt='*' \\
                -d fun='test.kwarg' -d arg='one=1' -d arg='two=2'

    :param entity: raw POST data
    '''
    if six.PY3:
        # https://github.com/cherrypy/cherrypy/pull/1572
        contents = six.StringIO()
        entity.fp.read(fp_out=contents)
        contents.seek(0)
        body_str = contents.read()
        body_bytes = salt.utils.stringutils.to_bytes(body_str)
        body_bytes = six.BytesIO(body_bytes)
        body_bytes.seek(0)
        # Patch fp
        entity.fp = body_bytes
        del contents
    # First call out to CherryPy's default processor
    cherrypy._cpreqbody.process_urlencoded(entity)
    cherrypy._cpreqbody.process_urlencoded(entity)
    cherrypy.serving.request.unserialized_data = entity.params
    cherrypy.serving.request.raw_body = ''