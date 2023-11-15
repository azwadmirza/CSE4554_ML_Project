    def _get_version(cls):
        """
        Returns VCS program version.
        """
        output = cls._popen(['version', '-q'])
        matches = cls.VERSION_RE.match(output)
        if matches is None:
            raise OSError(
                u'Failed to parse version string: {0}'.format(output)
            )
        return matches.group(1)