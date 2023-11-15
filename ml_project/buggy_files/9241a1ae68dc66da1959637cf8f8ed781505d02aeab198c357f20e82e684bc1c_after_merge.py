    def venv_bin(self, version=LATEST, bin='python'):
        """Return path to the virtualenv bin path, or a specific binary

        By default, return the path to the ``python`` binary in the virtual
        environment path. If ``bin`` is :py:data:`None`, then return the path to
        the virtual env path.
        """
        if bin is None:
            bin = ''
        return os.path.join(self.venv_path(version), 'bin', bin)