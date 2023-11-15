    def __init__(self, data_loader, size, batch_size):
        """
        Create a data generator wrapper on top of an MXNet :class:`DataLoader`.

        :param data_loader:
        :type data_loader: `mxnet.gluon.data.DataLoader`
        :param size: Total size of the dataset.
        :type size: int
        :param batch_size: Size of the minibatches.
        :type batch_size: int
        """
        from mxnet.gluon.data import DataLoader

        if not isinstance(data_loader, DataLoader):
            raise TypeError('Expected instance of Gluon `DataLoader, received %s instead.`' % str(type(data_loader)))

        self.data_loader = data_loader

        if size is not None and (type(size) is not int or size < 1):
            raise ValueError("The total size of the dataset must be an integer greater than zero.")

        self.size = size

        if type(batch_size) is not int or batch_size < 1:
            raise ValueError("The batch size must be an integer greater than zero.")

        self.batch_size = batch_size