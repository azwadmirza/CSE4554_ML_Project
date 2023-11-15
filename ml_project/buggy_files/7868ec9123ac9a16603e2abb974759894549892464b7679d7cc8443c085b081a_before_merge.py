    def snapshot(self, wiki=False, streamed=False, action=None,
                 chunk_size=1024, **kwargs):
        """Return a snapshot of the repository.

        Args:
            wiki (bool): If True return the wiki repository
            streamed (bool): If True the data will be processed by chunks of
                `chunk_size` and each chunk is passed to `action` for
                treatment.
            action (callable): Callable responsible of dealing with chunk of
                data
            chunk_size (int): Size of each chunk
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the content could not be retrieved

        Returns:
            str: The uncompressed tar archive of the repository
        """
        path = '/projects/%d/snapshot' % self.get_id()
        result = self.manager.gitlab.http_get(path, streamed=streamed,
                                              **kwargs)
        return utils.response_content(result, streamed, action, chunk_size)