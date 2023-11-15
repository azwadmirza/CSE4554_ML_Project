    def _transform(self, compose_list, data, targets):
        data = data / self.max_val
        args = [0, len(data.shape) - 1] + list(range(1, len(data.shape) - 1))
        data = torch.Tensor(data.transpose(*args))
        data_transforms = Compose(compose_list)
        return MultiTransformDataset(data, targets, data_transforms)