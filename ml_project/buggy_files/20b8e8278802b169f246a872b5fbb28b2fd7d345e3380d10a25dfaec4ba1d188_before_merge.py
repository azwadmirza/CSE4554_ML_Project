    def repository_raw_blob(self, sha, streamed=False, action=None,
                            chunk_size=1024, **kwargs):
        """Return the raw file contents for a blob.

        Args:
            sha(str): ID of the blob
            streamed (bool): If True the data will be processed by chunks of
                `chunk_size` and each chunk is passed to `action` for
                treatment
            action (callable): Callable responsible of dealing with chunk of
                data
            chunk_size (int): Size of each chunk
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the server failed to perform the request

        Returns:
            str: The blob content if streamed is False, None otherwise
        """
        path = '/projects/%s/repository/blobs/%s/raw' % (self.get_id(), sha)
        result = self.manager.gitlab.http_get(path, streamed=streamed,
                                              **kwargs)
        return utils.response_content(result, streamed, action, chunk_size)