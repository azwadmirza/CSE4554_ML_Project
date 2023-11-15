    def __repr__(self):
        """Return useful and verbose help."""
        return """\
<Nikola Commands>

    Sample usage:
    >>> commands.check('-l')

    Or, if you know the internal argument names:
    >>> commands.check(list=True)

Available commands: {0}.""".format(', '.join(self._cmdnames))