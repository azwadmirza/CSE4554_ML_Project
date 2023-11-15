    def set_image(self, *, url):
        """Sets the image for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing :attr:`Empty` removes the image.

        Parameters
        -----------
        url: :class:`str`
            The source URL for the image. Only HTTP(S) is supported.
        """

        if url is EmptyEmbed:
            del self._image
        else:
            self._image = {
                'url': str(url)
            }

        return self