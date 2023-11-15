    def merge(self, ancestor, other):
        assert other

        if ancestor:
            self._check_can_merge(ancestor)
            ancestor_info = ancestor.info
        else:
            ancestor_info = None

        self._check_can_merge(self)
        self._check_can_merge(other)

        self.info = self.cache.merge(ancestor_info, self.info, other.info)