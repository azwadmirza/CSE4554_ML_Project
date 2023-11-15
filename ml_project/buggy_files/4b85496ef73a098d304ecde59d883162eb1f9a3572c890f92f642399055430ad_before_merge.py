    def refresh(self):
        """Refresh the comment's attributes.

        If using :meth:`.Reddit.comment` this method must be called in order to
        obtain the comment's replies.

        """
        if 'context' in self.__dict__:  # Using hasattr triggers a fetch
            comment_path = self.context.split('?', 1)[0]
        else:
            comment_path = '{}_/{}'.format(
                self.submission._info_path(),  # pylint: disable=no-member
                self.id)

        # The context limit appears to be 8, but let's ask for more anyway.
        comment_list = self._reddit.get(comment_path,
                                        params={'context': 100})[1].children
        if not comment_list:
            raise ClientException(self.MISSING_COMMENT_MESSAGE)

        # With context, the comment may be nested so we have to find it
        comment = None
        queue = comment_list[:]
        while queue and (comment is None or comment.id != self.id):
            comment = queue.pop()
            queue.extend(comment._replies)

        if comment.id != self.id:
            raise ClientException(self.MISSING_COMMENT_MESSAGE)

        if self._submission is not None:
            del comment.__dict__['_submission']  # Don't replace if set
        self.__dict__.update(comment.__dict__)

        for reply in comment_list:
            reply.submission = self.submission
        return self