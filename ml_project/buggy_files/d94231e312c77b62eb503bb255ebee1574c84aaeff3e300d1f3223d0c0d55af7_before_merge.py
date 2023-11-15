    def show(self, title=None, port=0, address=None, websocket_origin=None,
             threaded=False, verbose=True, open=True, location=True, **kwargs):
        """
        Starts a Bokeh server and displays the Viewable in a new tab.

        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)
        port: int (optional, default=0)
          Allows specifying a specific port
        address : str
          The address the server should listen on for HTTP requests.
        websocket_origin: str or list(str) (optional)
          A list of hosts that can connect to the websocket.
          This is typically required when embedding a server app in
          an external web site.
          If None, "localhost" is used.
        threaded: boolean (optional, default=False)
          Whether to launch the Server on a separate thread, allowing
          interactive use.
        verbose: boolean (optional, default=True)
          Whether to print the address and port
        open : boolean (optional, default=True)
          Whether to open the server in a new browser tab
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.

        Returns
        -------
        server: bokeh.server.Server or threading.Thread
          Returns the Bokeh server instance or the thread the server
          was launched on (if threaded=True)
        """
        if threaded:
            from tornado.ioloop import IOLoop
            loop = IOLoop()
            server = StoppableThread(
                target=self._get_server, io_loop=loop,
                args=(port, address, websocket_origin, loop, open,
                      True, title, verbose, location),
                kwargs=kwargs)
            server.start()
        else:
            server = self._get_server(
                port, address, websocket_origin, show=open, start=True,
                title=title, verbose=verbose, location=location, **kwargs
            )
        return server