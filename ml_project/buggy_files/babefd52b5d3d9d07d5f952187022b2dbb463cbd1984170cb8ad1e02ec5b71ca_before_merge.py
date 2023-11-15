    def remove(self):
        for c in self:
            c.remove()

        if self._remove_method:
            self._remove_method(self)