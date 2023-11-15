    def repository_archive(self, sha=None, streamed=False, action=None,
                           chunk_size=1024, **kwargs):
        """Return a tarball of the repository.

        Args:
            sha (str): ID of the commit (default branch by default)
            streamed (bool): If True the data will be processed by chunks of
                `chunk_size` and each chunk is passed to `action` for
                treatment
            action (callable): Callable responsible of dealing with chunk of
                data
            chunk_size (int): Size of each chunk
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError: If the server failed to perform the request

        Returns:
            str: The binary data of the archive
        """
        path = '/projects/%s/repository/archive' % self.get_id()
        query_data = {}
        if sha:
            query_data['sha'] = sha
        result = self.manager.gitlab.http_get(path, query_data=query_data,
                                              raw=True, streamed=streamed,
                                              **kwargs)
        return utils.response_content(result, streamed, action, chunk_size)