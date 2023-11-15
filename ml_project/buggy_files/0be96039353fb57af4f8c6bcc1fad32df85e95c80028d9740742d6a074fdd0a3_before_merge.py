def get_root(app, request=None):
    """ Return a tuple composed of ``(root, closer)`` when provided a
    :term:`router` instance as the ``app`` argument.  The ``root``
    returned is the application root object.  The ``closer`` returned
    is a callable (accepting no arguments) that should be called when
    your scripting application is finished using the root.

    ``request`` is passed to the :app:`Pyramid` application root
    factory to compute the root. If ``request`` is None, a default
    will be constructed using the registry's :term:`Request Factory`
    via the :meth:`pyramid.interfaces.IRequestFactory.blank` method.
    """
    registry = app.registry
    if request is None:
        request = _make_request('/', registry)
    threadlocals = {'registry':registry, 'request':request}
    app.threadlocal_manager.push(threadlocals)
    def closer(request=request): # keep request alive via this function default
        app.threadlocal_manager.pop()
    root = app.root_factory(request)
    return root, closer