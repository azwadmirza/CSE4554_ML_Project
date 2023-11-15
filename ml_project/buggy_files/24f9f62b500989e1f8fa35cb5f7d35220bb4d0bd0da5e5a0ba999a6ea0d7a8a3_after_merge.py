    def transform_train(self, data, targets=None, batch_size=None):
        data = (data - self.mean) / self.std
        data = np.nan_to_num(data)
        dataset = self._transform([], data, targets)

        if batch_size is None:
            batch_size = Constant.MAX_BATCH_SIZE
        batch_size = min(len(data), batch_size)

        return DataLoader(dataset, batch_size=batch_size, shuffle=True)