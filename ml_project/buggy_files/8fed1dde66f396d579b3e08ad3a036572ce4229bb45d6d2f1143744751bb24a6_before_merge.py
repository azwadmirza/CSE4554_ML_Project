    def GET(self, token=None, salt_token=None):
        r'''
        An HTTP stream of the Salt master event bus

        This stream is formatted per the Server Sent Events (SSE) spec. Each
        event is formatted as JSON.

        .. http:get:: /events

            :status 200: |200|
            :status 401: |401|
            :status 406: |406|
            :query token: **optional** parameter containing the token
                ordinarily supplied via the X-Auth-Token header in order to
                allow cross-domain requests in browsers that do not include
                CORS support in the EventSource API. E.g.,
                ``curl -NsS localhost:8000/events?token=308650d``
            :query salt_token: **optional** parameter containing a raw Salt
                *eauth token* (not to be confused with the token returned from
                the /login URL). E.g.,
                ``curl -NsS localhost:8000/events?salt_token=30742765``

        **Example request:**

        .. code-block:: bash

            curl -NsS localhost:8000/events

        .. code-block:: http

            GET /events HTTP/1.1
            Host: localhost:8000

        **Example response:**

        Note, the ``tag`` field is not part of the spec. SSE compliant clients
        should ignore unknown fields. This addition allows non-compliant
        clients to only watch for certain tags without having to deserialze the
        JSON object each time.

        .. code-block:: http

            HTTP/1.1 200 OK
            Connection: keep-alive
            Cache-Control: no-cache
            Content-Type: text/event-stream;charset=utf-8

            retry: 400

            tag: salt/job/20130802115730568475/new
            data: {'tag': 'salt/job/20130802115730568475/new', 'data': {'minions': ['ms-4', 'ms-3', 'ms-2', 'ms-1', 'ms-0']}}

            tag: salt/job/20130802115730568475/ret/jerry
            data: {'tag': 'salt/job/20130802115730568475/ret/jerry', 'data': {'jid': '20130802115730568475', 'return': True, 'retcode': 0, 'success': True, 'cmd': '_return', 'fun': 'test.ping', 'id': 'ms-1'}}

        The event stream can be easily consumed via JavaScript:

        .. code-block:: javascript

            var source = new EventSource('/events');
            source.onopen = function() { console.info('Listening ...') };
            source.onerror = function(err) { console.error(err) };
            source.onmessage = function(message) {
              var saltEvent = JSON.parse(message.data);
              console.info(saltEvent.tag)
              console.debug(saltEvent.data)
            };

        Or using CORS:

        .. code-block:: javascript

            var source = new EventSource('/events?token=ecd589e4e01912cf3c4035afad73426dbb8dba75', {withCredentials: true});

        It is also possible to consume the stream via the shell.

        Records are separated by blank lines; the ``data:`` and ``tag:``
        prefixes will need to be removed manually before attempting to
        unserialize the JSON.

        curl's ``-N`` flag turns off input buffering which is required to
        process the stream incrementally.

        Here is a basic example of printing each event as it comes in:

        .. code-block:: bash

            curl -NsS localhost:8000/events |\
                    while IFS= read -r line ; do
                        echo $line
                    done

        Here is an example of using awk to filter events based on tag:

        .. code-block:: bash

            curl -NsS localhost:8000/events |\
                    awk '
                        BEGIN { RS=""; FS="\\n" }
                        $1 ~ /^tag: salt\/job\/[0-9]+\/new$/ { print $0 }
                    '
            tag: salt/job/20140112010149808995/new
            data: {"tag": "salt/job/20140112010149808995/new", "data": {"tgt_type": "glob", "jid": "20140112010149808995", "tgt": "jerry", "_stamp": "2014-01-12_01:01:49.809617", "user": "shouse", "arg": [], "fun": "test.ping", "minions": ["jerry"]}}
            tag: 20140112010149808995
            data: {"tag": "20140112010149808995", "data": {"fun_args": [], "jid": "20140112010149808995", "return": true, "retcode": 0, "success": true, "cmd": "_return", "_stamp": "2014-01-12_01:01:49.819316", "fun": "test.ping", "id": "jerry"}}
        '''
        cookies = cherrypy.request.cookie
        auth_token = token or salt_token or (
            cookies['session_id'].value if 'session_id' in cookies else None)

        if not self._is_valid_token(auth_token):
            raise cherrypy.HTTPError(401)

        # Release the session lock before starting the long-running response
        cherrypy.session.release_lock()

        cherrypy.response.headers['Content-Type'] = 'text/event-stream'
        cherrypy.response.headers['Cache-Control'] = 'no-cache'
        cherrypy.response.headers['Connection'] = 'keep-alive'

        def listen():
            '''
            An iterator to yield Salt events
            '''
            event = salt.utils.event.get_event(
                    'master',
                    sock_dir=self.opts['sock_dir'],
                    transport=self.opts['transport'],
                    opts=self.opts,
                    listen=True)
            stream = event.iter_events(full=True)

            yield u'retry: {0}\n'.format(400)

            while True:
                data = next(stream)
                yield u'tag: {0}\n'.format(data.get('tag', ''))
                yield u'data: {0}\n\n'.format(json.dumps(data))

        return listen()