def json_processor(entity):
    '''
    Unserialize raw POST data in JSON format to a Python data structure.

    :param entity: raw POST data
    '''
    if six.PY2:
        body = entity.fp.read()
    else:
        # https://github.com/cherrypy/cherrypy/pull/1572
        contents = BytesIO()
        body = entity.fp.read(fp_out=contents)
        contents.seek(0)
        body = salt.utils.stringutils.to_unicode(contents.read())
        del contents
    try:
        cherrypy.serving.request.unserialized_data = json.loads(body)
    except ValueError:
        raise cherrypy.HTTPError(400, 'Invalid JSON document')

    cherrypy.serving.request.raw_body = body