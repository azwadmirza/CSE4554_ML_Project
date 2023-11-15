    def __init__(self, session_id=None, websocket_url=DEFAULT_SERVER_WEBSOCKET_URL, io_loop=None):
        '''
        A connection which attaches to a particular named session on the server.

        Always call either pull() or push() immediately after creating the session
        (until these are called session.document will be None).

        The bokeh.client.push_session() and bokeh.client.pull_session() functions
        will construct a ClientSession and push or pull in one step, so they are
        a good way to obtain a ClientSession.

        Args:
            session_id (str) :
                The name of the session or None to generate one
            websocket_url (str) :
                Websocket URL to connect to
            io_loop (``tornado.ioloop.IOLoop``, optional) :
                The IOLoop to use for the websocket
        '''
        self._document = None
        self._id = self._ensure_session_id(session_id)

        self._connection = ClientConnection(session=self, io_loop=io_loop, websocket_url=websocket_url)

        self._current_patch = None
        self._callbacks = _DocumentCallbackGroup(self._connection.io_loop)