    def resize_shape(self, size: int) -> None:
        """ Resize the shape of the dataset by resizing each tensor first dimension """
        if size == self.shape[0]:
            return

        self._shape = (int(size),)
        self.meta = self._store_meta()
        for t in self._tensors.values():
            t.resize_shape(int(size))

        self._update_dataset_state()