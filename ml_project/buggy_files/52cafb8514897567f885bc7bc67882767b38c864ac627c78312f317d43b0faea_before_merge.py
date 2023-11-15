    def _get_version(cls):
        """
        Returns VCS program version.
        """
        output = cls._popen(['version', '-q'])
        return cls.VERSION_RE.match(output).group(1)