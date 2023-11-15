def view_lookup(request, uri):
    """
    Look-up the specified `uri` and return the associated resource name
    along the match dict.

    :param request: the current request (used to obtain registry).
    :param uri: a plural or object endpoint URI.
    :rtype: tuple
    :returns: the resource name and the associated matchdict.
    """
    api_prefix = '/%s' % request.upath_info.split('/')[1]
    # Path should be bytes in PY2, and unicode in PY3
    path = _encoded(api_prefix + uri)

    q = request.registry.queryUtility
    routes_mapper = q(IRoutesMapper)

    fakerequest = Request.blank(path=path)
    info = routes_mapper(fakerequest)
    matchdict, route = info['match'], info['route']
    resource_name = route.name.replace('-record', '')\
                              .replace('-collection', '')
    return resource_name, matchdict