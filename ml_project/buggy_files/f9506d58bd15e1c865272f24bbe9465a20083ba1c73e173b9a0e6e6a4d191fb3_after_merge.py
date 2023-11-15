    def merge(self, ancestor, other):
        assert other

        if ancestor:
            self._check_can_merge(ancestor)
            ancestor_info = ancestor.hash_info
        else:
            ancestor_info = None

        self._check_can_merge(self)
        self._check_can_merge(other)

        self.hash_info = self.cache.merge(
            ancestor_info, self.hash_info, other.hash_info
        )