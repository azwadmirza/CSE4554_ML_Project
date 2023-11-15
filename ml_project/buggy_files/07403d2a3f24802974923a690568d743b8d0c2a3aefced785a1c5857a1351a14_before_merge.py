    def stop(self, port):
        """
        Stop the flask web server by loading /shutdown.
        """

        if self.mode == 'share':
            # If the user cancels the download, let the download function know to stop
            # serving the file
            self.share_mode.client_cancel = True

        # To stop flask, load http://127.0.0.1:<port>/<shutdown_slug>/shutdown
        if self.running:
            try:
                s = socket.socket()
                s.connect(('127.0.0.1', port))
                s.sendall('GET /{0:s}/shutdown HTTP/1.1\r\n\r\n'.format(self.shutdown_slug))
            except:
                try:
                    urlopen('http://127.0.0.1:{0:d}/{1:s}/shutdown'.format(port, self.shutdown_slug)).read()
                except:
                    pass