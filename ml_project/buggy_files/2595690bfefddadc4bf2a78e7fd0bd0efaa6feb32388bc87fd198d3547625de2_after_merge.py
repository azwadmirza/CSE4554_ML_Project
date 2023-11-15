    def _get_unused_port(self, close_on_exit=True):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]

        # Try to generate a port that is far above the 'next available' one.
        # This solves issue #8254 where GRPC fails because the port assigned
        # from this method has been used by a different process.
        for _ in range(NUMBER_OF_PORT_RETRIES):
            new_port = random.randint(port, 65535)
            new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                new_s.bind(("", new_port))
            except OSError:
                new_s.close()
                continue
            s.close()
            if close_on_exit:
                new_s.close()
            return new_port, new_s
        logger.error("Unable to succeed in selecting a random port.")
        if close_on_exit:
            s.close()
        return port, s