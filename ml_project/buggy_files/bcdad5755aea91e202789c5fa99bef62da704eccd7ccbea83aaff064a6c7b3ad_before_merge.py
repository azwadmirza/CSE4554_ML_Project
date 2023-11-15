    def _accept(self):
        """ Listen for connections and pass handling to a new thread """
        while True:
            (client, address) = self.sock.accept()
            thread = threading.Thread(target=self._handle_conn,
                                      args=(client, address))
            thread.daemon = True
            thread.start()