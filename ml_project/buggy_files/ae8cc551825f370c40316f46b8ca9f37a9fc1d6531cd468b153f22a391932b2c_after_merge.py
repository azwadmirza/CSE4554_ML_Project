    def exec_start(self, exec_id, detach=False, tty=False, stream=False,
                   socket=False):
        """
        Start a previously set up exec instance.

        Args:
            exec_id (str): ID of the exec instance
            detach (bool): If true, detach from the exec command.
                Default: False
            tty (bool): Allocate a pseudo-TTY. Default: False
            stream (bool): Stream response data. Default: False

        Returns:
            (generator or str): If ``stream=True``, a generator yielding
            response chunks. A string containing response data otherwise.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        # we want opened socket if socket == True
        if isinstance(exec_id, dict):
            exec_id = exec_id.get('Id')

        data = {
            'Tty': tty,
            'Detach': detach
        }

        headers = {} if detach else {
            'Connection': 'Upgrade',
            'Upgrade': 'tcp'
        }

        res = self._post_json(
            self._url('/exec/{0}/start', exec_id),
            headers=headers,
            data=data,
            stream=True
        )
        if detach:
            return self._result(res)
        if socket:
            return self._get_raw_response_socket(res)
        return self._read_from_socket(res, stream)