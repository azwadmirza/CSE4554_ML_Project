    def to_dict(self, trim=True):
        if trim:
            return self._to_trimmed_dict()
        else:
            return dict(zip(DATASET_KEYS, self))