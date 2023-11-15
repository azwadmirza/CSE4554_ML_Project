    def __init__(self, key_prefixes):
        key_prefixes = map(self._sanitize, key_prefixes)
        # compute read and write dirs from base runtime dirs: the first base
        # dir is selected for writes and prefered for reads
        self._read_dirs = [os.path.join(x, *key_prefixes) for x in get_runtime_dirs()]
        self._write_dir = self._read_dirs[0]
        os.makedirs(self._write_dir, exist_ok=True)
        if sys.platform == 'linux':
            # set the sticky bit to prevent removal during cleanup
            os.chmod(self._write_dir, 0o1700)
        _LOGGER.debug('data in %s', self._write_dir)