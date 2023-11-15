def text_processor(entity):
    '''
    Attempt to unserialize plain text as JSON

    Some large services still send JSON with a text/plain Content-Type. Those
    services are bad and should feel bad.

    :param entity: raw POST data
    '''
    if six.PY2:
        body = entity.fp.read()
    else:
        # https://github.com/cherrypy/cherrypy/pull/1572
        contents = six.StringIO()
        body = entity.fp.read(fp_out=contents)
        contents.seek(0)
        body = contents.read()
    try:
        cherrypy.serving.request.unserialized_data = json.loads(body)
    except ValueError:
        cherrypy.serving.request.unserialized_data = body

    cherrypy.serving.request.raw_body = body