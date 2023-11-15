        def do_GET(self):
            """Process a request from an HTML browser.

            The URL received is in self.path.
            Get an HTML page from self.urlhandler and send it.
            """
            if self.path.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'text/html'
            self.send_response(200)
            self.send_header(
                'Content-Type', '%s; charset=UTF-8' % content_type)
            self.end_headers()
            try:
                self.wfile.write(self.urlhandler(
                    self.path, content_type).encode('utf-8'))
            except ConnectionAbortedError:
                # Needed to handle error when client closes the connection,
                # for example when the client stops the load of the previously
                # requested page. See spyder-ide/spyder#10755
                pass
            except BrokenPipeError:
                pass