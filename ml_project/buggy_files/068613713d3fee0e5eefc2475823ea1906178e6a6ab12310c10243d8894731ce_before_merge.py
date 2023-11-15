    def __init__(self, file_path):
        self._file_path = file_path
        self._fd = None
        self._reads = 0
        self._writes = 0