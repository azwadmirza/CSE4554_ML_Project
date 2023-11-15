def yaml_processor(entity):
    '''
    Unserialize raw POST data in YAML format to a Python data structure.

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
        cherrypy.serving.request.unserialized_data = yaml.safe_load(body)
    except ValueError:
        raise cherrypy.HTTPError(400, 'Invalid YAML document')

    cherrypy.serving.request.raw_body = body