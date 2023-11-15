    def pull(self, repository, tag=None, **kwargs):
        """
        Pull an image of the given name and return it. Similar to the
        ``docker pull`` command.
        If no tag is specified, all tags from that repository will be
        pulled.

        If you want to get the raw pull output, use the
        :py:meth:`~docker.api.image.ImageApiMixin.pull` method in the
        low-level API.

        Args:
            repository (str): The repository to pull
            tag (str): The tag to pull
            auth_config (dict): Override the credentials that
                :py:meth:`~docker.client.DockerClient.login` has set for
                this request. ``auth_config`` should contain the ``username``
                and ``password`` keys to be valid.
            platform (str): Platform in the format ``os[/arch[/variant]]``

        Returns:
            (:py:class:`Image` or list): The image that has been pulled.
                If no ``tag`` was specified, the method will return a list
                of :py:class:`Image` objects belonging to this repository.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.

        Example:

            >>> # Pull the image tagged `latest` in the busybox repo
            >>> image = client.images.pull('busybox:latest')

            >>> # Pull all tags in the busybox repo
            >>> images = client.images.pull('busybox')
        """
        if not tag:
            repository, tag = parse_repository_tag(repository)

        self.client.api.pull(repository, tag=tag, **kwargs)
        if tag:
            return self.get('{0}{2}{1}'.format(
                repository, tag, '@' if tag.startswith('sha256:') else ':'
            ))
        return self.list(repository)