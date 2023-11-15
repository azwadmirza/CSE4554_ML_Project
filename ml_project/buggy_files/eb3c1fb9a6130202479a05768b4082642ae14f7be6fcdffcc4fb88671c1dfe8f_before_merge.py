    def get(self):
        r"""
        An HTTP stream of the Salt master event bus

        This stream is formatted per the Server Sent Events (SSE) spec. Each
        event is formatted as JSON.

        .. http:get:: /events

            :status 200: |200|
            :status 401: |401|
            :status 406: |406|

        **Example request:**

        .. code-block:: bash

            curl -NsS localhost:8000/events

        .. code-block:: text

            GET /events HTTP/1.1
            Host: localhost:8000

        **Example response:**

        .. code-block:: text

            HTTP/1.1 200 OK
            Connection: keep-alive
            Cache-Control: no-cache
            Content-Type: text/event-stream;charset=utf-8

            retry: 400
            data: {'tag': '', 'data': {'minions': ['ms-4', 'ms-3', 'ms-2', 'ms-1', 'ms-0']}}

            data: {'tag': '20130802115730568475', 'data': {'jid': '20130802115730568475', 'return': True, 'retcode': 0, 'success': True, 'cmd': '_return', 'fun': 'test.ping', 'id': 'ms-1'}}

        The event stream can be easily consumed via JavaScript:

        .. code-block:: javascript

            <!-- Note, you must be authenticated! -->
            var source = new EventSource('/events');
            source.onopen = function() { console.debug('opening') };
            source.onerror = function(e) { console.debug('error!', e) };
            source.onmessage = function(e) { console.debug(e.data) };

        Or using CORS:

        .. code-block:: javascript

            var source = new EventSource('/events', {withCredentials: true});

        Some browser clients lack CORS support for the ``EventSource()`` API. Such
        clients may instead pass the :mailheader:`X-Auth-Token` value as an URL
        parameter:

        .. code-block:: bash

            curl -NsS localhost:8000/events/6d1b722e

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
        """
        # if you aren't authenticated, redirect to login
        if not self._verify_auth():
            self.redirect("/login")
            return
        # set the streaming headers
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        self.write("retry: {0}\n".format(400))
        self.flush()

        while True:
            try:
                event = yield self.application.event_listener.get_event(self)
                self.write("tag: {0}\n".format(event.get("tag", "")))
                self.write(
                    str("data: {0}\n\n").format(_json_dumps(event))
                )  # future lint: disable=blacklisted-function
                self.flush()
            except TimeoutException:
                break