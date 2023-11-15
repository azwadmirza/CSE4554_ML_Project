    def run(self):
        import pydoc
        if PY3:
            # Python 3
            self.callback(pydoc._start_server(pydoc._url_handler, self.port))
        else:
            # Python 2
            pydoc.serve(self.port, self.callback, self.completer)