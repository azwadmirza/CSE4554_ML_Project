        def accept_worker():
            while True:
                try:
                    sock, (other_host, other_port) = cls.listener.accept()
                except OSError:
                    # Listener socket has been closed.
                    break

                log.info(
                    "Accepted incoming {0} connection from {1}:{2}.",
                    name,
                    other_host,
                    other_port,
                )
                cls(sock)