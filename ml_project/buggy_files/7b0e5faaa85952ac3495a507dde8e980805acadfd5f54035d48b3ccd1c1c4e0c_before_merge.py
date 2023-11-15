    def __init__(self, src, must_symlink, must_copy):
        self.must_symlink = must_symlink
        self.must_copy = must_copy
        self.src = src
        self.exists = src.exists()
        self._can_read = None if self.exists else False
        self._can_copy = None if self.exists else False
        self._can_symlink = None if self.exists else False
        if self.must_copy is True and self.must_symlink is True:
            raise ValueError("can copy and symlink at the same time")