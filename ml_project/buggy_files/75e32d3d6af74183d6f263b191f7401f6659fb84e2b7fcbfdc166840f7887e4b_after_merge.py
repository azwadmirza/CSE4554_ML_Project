    def app(self_or_cls, plot, show=False, new_window=False, websocket_origin=None):
        """
        Creates a bokeh app from a HoloViews object or plot. By
        default simply attaches the plot to bokeh's curdoc and returns
        the Document, if show option is supplied creates an
        Application instance and displays it either in a browser
        window or inline if notebook extension has been loaded.  Using
        the new_window option the app may be displayed in a new
        browser tab once the notebook extension has been loaded.  A
        websocket origin is required when launching from an existing
        tornado server (such as the notebook) and it is not on the
        default port ('localhost:8888').
        """
        renderer = self_or_cls.instance(mode='server')
        # If show=False and not in notebook context return document
        if not show and not self_or_cls.notebook_context:
            doc, _ = renderer(plot)
            return doc

        def modify_doc(doc):
            renderer(plot, doc=doc)
        handler = FunctionHandler(modify_doc)
        app = Application(handler)

        if not show:
            # If not showing and in notebook context return app
            return app
        elif self_or_cls.notebook_context and not new_window:
            # If in notebook, show=True and no new window requested
            # display app inline
            opts = dict(notebook_url=websocket_origin) if websocket_origin else {}
            return bkshow(app, **opts)

        # If app shown outside notebook or new_window requested
        # start server and open in new browser tab
        from tornado.ioloop import IOLoop
        loop = IOLoop.current()
        opts = dict(allow_websocket_origin=[websocket_origin]) if websocket_origin else {}
        opts['io_loop' if bokeh_version > '0.12.7' else 'loop'] = loop
        server = Server({'/': app}, port=0, **opts)
        def show_callback():
            server.show('/')
        server.io_loop.add_callback(show_callback)
        server.start()
        try:
            loop.start()
        except RuntimeError:
            pass
        return server