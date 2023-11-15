    def _prepare_socket_file(self, socket_path, default_prefix):
        """Prepare the socket file for raylet and plasma.

        This method helps to prepare a socket file.
        1. Make the directory if the directory does not exist.
        2. If the socket file exists, raise exception.

        Args:
            socket_path (string): the socket file to prepare.
        """
        result = socket_path
        is_mac = sys.platform.startswith("darwin")
        if sys.platform == "win32":
            if socket_path is None:
                result = "tcp://{}:{}".format(self._localhost,
                                              self._get_unused_port()[0])
        else:
            if socket_path is None:
                result = self._make_inc_temp(
                    prefix=default_prefix, directory_name=self._sockets_dir)
            else:
                if os.path.exists(socket_path):
                    raise RuntimeError(
                        "Socket file {} exists!".format(socket_path))
                try_to_create_directory(os.path.dirname(socket_path))

            # Check socket path length to make sure it's short enough
            maxlen = (104 if is_mac else 108) - 1  # sockaddr_un->sun_path
            if len(result.split("://", 1)[-1].encode("utf-8")) > maxlen:
                raise OSError("AF_UNIX path length cannot exceed "
                              "{} bytes: {!r}".format(maxlen, result))
        return result