    def write(self, logentry):
        for i in list(logentry.keys()):
            # Remove twisted 15 legacy keys
            if i.startswith('log_'):
                del logentry[i]

        message = json.dumps(logentry) + '\n'

        try:
            self.sock.sendall(message)
        except socket.error as ex:
            if ex.errno == 32:  # Broken pipe
                self.start()
                self.sock.sendall(message)
            else:
                raise