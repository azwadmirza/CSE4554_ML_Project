    def pull(self, repository, tag=None, stream=False, auth_config=None,
             decode=False, platform=None):
        """
        Pulls an image. Similar to the ``docker pull`` command.

        Args:
            repository (str): The repository to pull
            tag (str): The tag to pull
            stream (bool): Stream the output as a generator
            auth_config (dict): Override the credentials that
                :py:meth:`~docker.api.daemon.DaemonApiMixin.login` has set for
                this request. ``auth_config`` should contain the ``username``
                and ``password`` keys to be valid.
            decode (bool): Decode the JSON data from the server into dicts.
                Only applies with ``stream=True``
            platform (str): Platform in the format ``os[/arch[/variant]]``

        Returns:
            (generator or str): The output

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.

        Example:

            >>> for line in cli.pull('busybox', stream=True):
            ...     print(json.dumps(json.loads(line), indent=4))
            {
                "status": "Pulling image (latest) from busybox",
                "progressDetail": {},
                "id": "e72ac664f4f0"
            }
            {
                "status": "Pulling image (latest) from busybox, endpoint: ...",
                "progressDetail": {},
                "id": "e72ac664f4f0"
            }

        """
        if not tag:
            repository, tag = utils.parse_repository_tag(repository)
        registry, repo_name = auth.resolve_repository_name(repository)

        params = {
            'tag': tag,
            'fromImage': repository
        }
        headers = {}

        if auth_config is None:
            header = auth.get_config_header(self, registry)
            if header:
                headers['X-Registry-Auth'] = header
        else:
            log.debug('Sending supplied auth config')
            headers['X-Registry-Auth'] = auth.encode_header(auth_config)

        if platform is not None:
            if utils.version_lt(self._version, '1.32'):
                raise errors.InvalidVersion(
                    'platform was only introduced in API version 1.32'
                )
            params['platform'] = platform

        response = self._post(
            self._url('/images/create'), params=params, headers=headers,
            stream=stream, timeout=None
        )

        self._raise_for_status(response)

        if stream:
            return self._stream_helper(response, decode=decode)

        return self._result(response)