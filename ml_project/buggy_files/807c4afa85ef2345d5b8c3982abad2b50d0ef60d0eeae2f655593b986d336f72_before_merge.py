    def add_url(self, url, title="", *, redirect=False, atime=None):
        """Called via add_from_tab when a URL should be added to the history.

        Args:
            url: A url (as QUrl) to add to the history.
            redirect: Whether the entry was redirected to another URL
                      (hidden in completion)
            atime: Override the atime used to add the entry
        """
        if not url.isValid():
            log.misc.warning("Ignoring invalid URL being added to history")
            return

        if 'no-sql-history' in objreg.get('args').debug_flags:
            return

        atime = int(atime) if (atime is not None) else int(time.time())
        self.insert({'url': self._format_url(url),
                     'title': title,
                     'atime': atime,
                     'redirect': redirect})
        if not redirect:
            self.completion.insert({'url': self._format_completion_url(url),
                                    'title': title,
                                    'last_atime': atime},
                                   replace=True)