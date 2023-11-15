    def __init__(self, data_loader, size, batch_size):
        """
        Create a data generator wrapper on top of a PyTorch :class:`DataLoader`.
        :param data_loader: A PyTorch data generator.
        :type data_loader: `torch.utils.data.DataLoader`
        :param size: Total size of the dataset.
        :type size: int
        :param batch_size: Size of the minibatches.
        :type batch_size: int
        """
        super(PyTorchDataGenerator, self).__init__(size=size, batch_size=batch_size)

        from torch.utils.data import DataLoader

        if not isinstance(data_loader, DataLoader):
            raise TypeError('Expected instance of PyTorch `DataLoader, received %s instead.`' % str(type(data_loader)))

        self.data_loader = data_loader