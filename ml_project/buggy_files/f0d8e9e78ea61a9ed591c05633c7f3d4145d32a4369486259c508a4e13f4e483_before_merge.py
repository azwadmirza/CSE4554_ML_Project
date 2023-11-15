    def GET(self, token=None, **kwargs):
        '''
        Return a websocket connection of Salt's event stream

        .. http:get:: /ws/(token)

        :query format_events: The event stream will undergo server-side
            formatting if the ``format_events`` URL parameter is included
            in the request. This can be useful to avoid formatting on the
            client-side:

            .. code-block:: bash

                curl -NsS <...snip...> localhost:8000/ws?format_events

        :reqheader X-Auth-Token: an authentication token from
            :py:class:`~Login`.

        :status 101: switching to the websockets protocol
        :status 401: |401|
        :status 406: |406|

        **Example request:** ::

            curl -NsSk \\
                -H 'X-Auth-Token: ffedf49d' \\
                -H 'Host: localhost:8000' \\
                -H 'Connection: Upgrade' \\
                -H 'Upgrade: websocket' \\
                -H 'Origin: https://localhost:8000' \\
                -H 'Sec-WebSocket-Version: 13' \\
                -H 'Sec-WebSocket-Key: '"$(echo -n $RANDOM | base64)" \\
                localhost:8000/ws

        .. code-block:: http

            GET /ws HTTP/1.1
            Connection: Upgrade
            Upgrade: websocket
            Host: localhost:8000
            Origin: https://localhost:8000
            Sec-WebSocket-Version: 13
            Sec-WebSocket-Key: s65VsgHigh7v/Jcf4nXHnA==
            X-Auth-Token: ffedf49d

        **Example response**:

        .. code-block:: http

            HTTP/1.1 101 Switching Protocols
            Upgrade: websocket
            Connection: Upgrade
            Sec-WebSocket-Accept: mWZjBV9FCglzn1rIKJAxrTFlnJE=
            Sec-WebSocket-Version: 13

        An authentication token **may optionally** be passed as part of the URL
        for browsers that cannot be configured to send the authentication
        header or cookie:

        .. code-block:: bash

            curl -NsS <...snip...> localhost:8000/ws/ffedf49d

        The event stream can be easily consumed via JavaScript:

        .. code-block:: javascript

            // Note, you must be authenticated!
            var source = new Websocket('ws://localhost:8000/ws/d0ce6c1a');
            source.onerror = function(e) { console.debug('error!', e); };
            source.onmessage = function(e) { console.debug(e.data); };

            source.send('websocket client ready')

            source.close();

        Or via Python, using the Python module `websocket-client
        <https://pypi.python.org/pypi/websocket-client/>`_ for example.

        .. code-block:: python

            # Note, you must be authenticated!

            from websocket import create_connection

            ws = create_connection('ws://localhost:8000/ws/d0ce6c1a')
            ws.send('websocket client ready')

            # Look at https://pypi.python.org/pypi/websocket-client/ for more
            # examples.
            while listening_to_events:
                print ws.recv()

            ws.close()

        Above examples show how to establish a websocket connection to Salt and
        activating real time updates from Salt's event stream by signaling
        ``websocket client ready``.
        '''
        # Pulling the session token from an URL param is a workaround for
        # browsers not supporting CORS in the EventSource API.
        if token:
            orig_sesion, _ = cherrypy.session.cache.get(token, ({}, None))
            salt_token = orig_sesion.get('token')
        else:
            salt_token = cherrypy.session.get('token')

        # Manually verify the token
        if not salt_token or not self.auth.get_tok(salt_token):
            raise cherrypy.HTTPError(401)

        # Release the session lock before starting the long-running response
        cherrypy.session.release_lock()

        # A handler is the server side end of the websocket connection. Each
        # request spawns a new instance of this handler
        handler = cherrypy.request.ws_handler

        def event_stream(handler, pipe):
            '''
            An iterator to return Salt events (and optionally format them)
            '''
            # blocks until send is called on the parent end of this pipe.
            pipe.recv()

            event = salt.utils.event.get_event(
                    'master',
                    sock_dir=self.opts['sock_dir'],
                    transport=self.opts['transport'],
                    opts=self.opts,
                    listen=True)
            stream = event.iter_events(full=True)
            SaltInfo = event_processor.SaltInfo(handler)
            while True:
                data = next(stream)
                if data:
                    try:  # work around try to decode catch unicode errors
                        if 'format_events' in kwargs:
                            SaltInfo.process(data, salt_token, self.opts)
                        else:
                            handler.send('data: {0}\n\n'.format(
                                json.dumps(data)), False)
                    except UnicodeDecodeError:
                        logger.error(
                                "Error: Salt event has non UTF-8 data:\n{0}"
                                .format(data))
                time.sleep(0.1)

        parent_pipe, child_pipe = Pipe()
        handler.pipe = parent_pipe
        handler.opts = self.opts
        # Process to handle async push to a client.
        # Each GET request causes a process to be kicked off.
        proc = Process(target=event_stream, args=(handler, child_pipe))
        proc.start()