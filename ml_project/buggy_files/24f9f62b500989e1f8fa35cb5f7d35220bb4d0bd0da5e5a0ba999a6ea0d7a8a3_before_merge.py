    def transform_train(self, data, targets=None, batch_size=None):
        dataset = self._transform([Normalize(torch.Tensor(self.mean), torch.Tensor(self.std))], data, targets)

        if batch_size is None:
            batch_size = Constant.MAX_BATCH_SIZE
        batch_size = min(len(data), batch_size)

        return DataLoader(dataset, batch_size=batch_size, shuffle=True)