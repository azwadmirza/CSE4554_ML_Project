    def __repr__(self):
        """Provide a representation for programmers."""
        header = '<TranslatableSetting> '

        if not self.translated:
            values = [repr(self())]
        else:
            values = ['{0}={1!r}'.format(k, v) for k, v in self.values.items()]

        return header + ', '.join(values)