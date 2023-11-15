    def attach(self, container, stdout=True, stderr=True,
               stream=False, logs=False):
        """
        Attach to a container.

        The ``.logs()`` function is a wrapper around this method, which you can
        use instead if you want to fetch/stream container output without first
        retrieving the entire backlog.

        Args:
            container (str): The container to attach to.
            stdout (bool): Include stdout.
            stderr (bool): Include stderr.
            stream (bool): Return container output progressively as an iterator
                of strings, rather than a single string.
            logs (bool): Include the container's previous output.

        Returns:
            By default, the container's output as a single string.

            If ``stream=True``, an iterator of output strings.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        params = {
            'logs': logs and 1 or 0,
            'stdout': stdout and 1 or 0,
            'stderr': stderr and 1 or 0,
            'stream': stream and 1 or 0
        }

        headers = {
            'Connection': 'Upgrade',
            'Upgrade': 'tcp'
        }

        u = self._url("/containers/{0}/attach", container)
        response = self._post(u, headers=headers, params=params, stream=stream)

        return self._read_from_socket(
            response, stream, self._check_is_tty(container)
        )