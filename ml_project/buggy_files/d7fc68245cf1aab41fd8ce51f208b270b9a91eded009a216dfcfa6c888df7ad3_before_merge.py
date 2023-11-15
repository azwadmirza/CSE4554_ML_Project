    def raw(self, file_path, ref, streamed=False, action=None, chunk_size=1024,
            **kwargs):
        """Return the content of a file for a commit.

        Args:
            ref (str): ID of the commit
            filepath (str): Path of the file to return
            streamed (bool): If True the data will be processed by chunks of
                `chunk_size` and each chunk is passed to `action` for
                treatment
            action (callable): Callable responsible of dealing with chunk of
                data
            chunk_size (int): Size of each chunk
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the file could not be retrieved

        Returns:
            str: The file content
        """
        file_path = file_path.replace('/', '%2F').replace('.', '%2E')
        path = '%s/%s/raw' % (self.path, file_path)
        query_data = {'ref': ref}
        result = self.gitlab.http_get(path, query_data=query_data,
                                      streamed=streamed, **kwargs)
        return utils.response_content(result, streamed, action, chunk_size)