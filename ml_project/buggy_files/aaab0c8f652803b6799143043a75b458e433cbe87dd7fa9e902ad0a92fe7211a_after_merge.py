    def run(self):
        import pydoc
        if PY3:
            # Python 3
            try:
                self.callback(pydoc._start_server(pydoc._url_handler,
                                                  port=self.port))
            except TypeError:
                # Python 3.7
                self.callback(pydoc._start_server(pydoc._url_handler,
                                                  hostname='localhost',
                                                  port=self.port))
        else:
            # Python 2
            pydoc.serve(self.port, self.callback, self.completer)