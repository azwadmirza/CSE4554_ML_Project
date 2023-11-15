    def __call__(self, *args):
        self.args = args
        if not self.dirty:
            self.dirty = True
            self._id = self.do_idle_add(self._wrap)