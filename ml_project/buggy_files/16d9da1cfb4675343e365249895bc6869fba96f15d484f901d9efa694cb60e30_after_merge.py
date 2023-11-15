    def execute(self, cmd, timeout=200, capture_output=True):
        """
        Executes a HAProxy command by sending a message to a HAProxy's local
        UNIX socket and waiting up to 'timeout' milliseconds for the response.
        """
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client.connect(self.socket)
        self.client.sendall(to_bytes('%s\n' % cmd))

        result = b''
        buf = b''
        buf = self.client.recv(RECV_SIZE)
        while buf:
            result += buf
            buf = self.client.recv(RECV_SIZE)
        result = to_text(result, errors='surrogate_or_strict')

        if capture_output:
            self.capture_command_output(cmd, result.strip())
        self.client.close()
        return result