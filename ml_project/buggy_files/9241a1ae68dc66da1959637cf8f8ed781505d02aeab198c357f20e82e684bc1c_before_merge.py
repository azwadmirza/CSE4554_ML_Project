    def venv_bin(self, version=LATEST, bin='python'):
        return os.path.join(self.venv_path(version), 'bin', bin)