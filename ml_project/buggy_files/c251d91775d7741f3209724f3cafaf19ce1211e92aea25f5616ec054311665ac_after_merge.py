    def __repr__(self):
        # In addition to saving values onto self, SklLearners save into params
        with patch.dict(self.__dict__, self.params):
            return super().__repr__()