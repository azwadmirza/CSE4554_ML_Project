def autoload_server(model=None, app_path=None, session_id=None, url="default", relative_urls=False):
    ''' Return a script tag that embeds content from a Bokeh server session.

    Bokeh apps embedded using ``autoload_server`` will NOT set the browser
    window title.

    .. note::
        Typically you will not want to save or re-use the output of this
        function for different or multiple page loads.

    Args:
        model (Model, optional) : The object to render from the session

            If ``None`` an entire document is rendered. (default: ``None``)

            If you supply a specific model to render, you must also supply the
            session ID containing that model.

            Supplying a model is usually only useful when embedding
            a specific session that was previously created using the
            ``bokeh.client`` API.

        session_id (str, optional) : A server session ID (default: None)

            If ``None``, let the server auto-generate a random session ID.

            Supplying a session id is usually only useful when embedding
            a specific session that was previously created using the
            ``bokeh.client`` API.

        url (str, optional) : A URL to a Bokeh application on a Bokeh server

            If ``None`` the default URL ``{DEFAULT_SERVER_HTTP_URL}`` will be used.

        relative_urls (bool, optional) :
            Whether to use relative URLs for resources.

            If ``True`` the links generated for resources such a BokehJS
            JavaScript and CSS will be relative links.

            This should normally be set to ``False``, but must be set to
            ``True`` in situations where only relative URLs will work. E.g.
            when running the Bokeh behind reverse-proxies under certain
            configurations

    Returns:
        A ``<script>`` tag that will execute an autoload script loaded
        from the Bokeh Server.

    Examples:

        In the simplest and most common case, we wish to embed Bokeh server
        application by providing the URL to where it is located.

        Suppose the app is running (perhaps behind Nginx or some other proxy)
        at ``http://app.server.org/foo/myapp``. We wish to embed this app in
        a page at ``mysite.com``. The following will provide an HTML script
        tag to do that, that can be included in ``mysite.com``:

        .. code-block:: python

            script = autoload_server(url="http://app.server.org/foo/myapp")

        Note that in order for this embedding to work, the Bokeh server needs
        to have been configured to allow connections from the public URL where
        the embedding happens. In this case, if the autoload script is run from
        a page located at ``http://mysite.com/report`` then the Bokeh server
        must have been started with an ``--allow-websocket-origin`` option
        specifically allowing websocket connections from pages that originate
        from ``mysite.com``:

        .. code-block:: sh

            bokeh serve mayapp.py --allow-websocket-origin=mysite.com

        If an autoload script runs from an origin that has not been allowed,
        the Bokeh server will return a 403 error.

        It's also possible to initiate sessions on a Bokeh server from
        Python, using the functions :func:`~bokeh.client.push_session` and
        :func:`~bokeh.client.push_session`. This can be useful in advanced
        situations where you may want to "set up" the session before you
        embed it. For example, you might to load up a session and modify
        ``session.document`` in some way (perhaps adding per-user data).

        In such cases you will pass the session id as an argument as well:

        .. code-block:: python

            script = autoload_server(session_id="some_session_id",
                                     url="http://app.server.org/foo/myapp")

        .. warning::
            It is typically a bad idea to re-use the same ``session_id`` for
            every page load. This is likely to create scalability and security
            problems, and will cause "shared Google doc" behaviour, which is
            typically not desired.

    '''
    if app_path is not None:
        deprecated((0, 12, 5), "app_path", "url", "Now pass entire app URLS in the url arguments, e.g. 'url=http://foo.com:5010/bar/myapp'")
        if not app_path.startswith("/"):
            app_path = "/" + app_path
        url = url + app_path

    coords = _SessionCoordinates(url=url, session_id=session_id)

    elementid = make_id()

    # empty model_id means render the entire doc from session_id
    model_id = ""
    if model is not None:
        model_id = model._id

    if model_id and session_id is None:
        raise ValueError("A specific model was passed to autoload_server() but no session_id; "
                         "this doesn't work because the server will generate a fresh session "
                         "which won't have the model in it.")

    src_path = coords.url + "/autoload.js?bokeh-autoload-element=" + elementid

    if url != "default":
        app_path = urlparse(url).path.rstrip("/")
        if not app_path.startswith("/"):
            app_path = "/" + app_path
        src_path += "&bokeh-app-path=" + app_path

    if not relative_urls:
        src_path += "&bokeh-absolute-url=" + coords.url

    # we want the server to generate the ID, so the autoload script
    # can be embedded in a static page while every user still gets
    # their own session. So we omit bokeh-session-id rather than
    # using a generated ID.
    if coords.session_id_allowing_none is not None:
        src_path = src_path + "&bokeh-session-id=" + session_id

    tag = AUTOLOAD_TAG.render(
        src_path = src_path,
        app_path = app_path,
        elementid = elementid,
        modelid = model_id,
    )

    return encode_utf8(tag)