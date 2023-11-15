    def _accept(self):
        """ Listen for connections and pass handling to a new thread """
        while True:
            try:
                (client, address) = self.sock.accept()
                thread = threading.Thread(target=self._handle_conn,
                                          args=(client, address))
                thread.daemon = True
                thread.start()
            except ConnectionAbortedError:
                # Workaround for #278
                print("A connection establish request was performed on a closed socket")
                return