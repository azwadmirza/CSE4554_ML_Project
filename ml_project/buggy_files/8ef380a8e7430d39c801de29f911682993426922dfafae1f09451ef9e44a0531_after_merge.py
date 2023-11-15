    def Dataset(path=None, name=None, train=True, input_size=224, crop_ratio=0.875, *args, **kwargs):
        """Dataset for AutoGluon image classification tasks.
           May either be a :class:`autogluon.task.image_classification.ImageFolderDataset`, :class:`autogluon.task.image_classification.RecordDataset`,
           or a popular dataset already built into AutoGluon ('mnist', 'fashionmnist', 'cifar10', 'cifar100', 'imagenet').

        Parameters
        ----------
        path : str, optional
            The data location. If using :class:`ImageFolderDataset`,
            image folder`path/to/the/folder` should be provided.
            If using :class:`RecordDataset`, the `path/to/*.rec` should be provided.
        name : str, optional
            Which built-in dataset to use, will override all other options if specified.
            The options are: 'mnist', 'fashionmnist', 'cifar', 'cifar10', 'cifar100', 'imagenet'
        train : bool, optional, default = True
            Whether this dataset should be used for training or validation.
        input_size : int
            The input image size.
        crop_ratio : float
            Center crop ratio (for evaluation only).

        Returns
        -------
        Dataset object that can be passed to `task.fit()`, which is actually an :class:`autogluon.space.AutoGluonObject`.
        To interact with such an object yourself, you must first call `Dataset.init()` to instantiate the object in Python.
        """
        if name is None:
            if path is None:
                raise ValueError("Either `path` or `name` must be present in Dataset(). "
                                 "If `name` is provided, it will override the rest of the arguments.")
        return get_dataset(path=path, train=train, name=name,
                           input_size=input_size, crop_ratio=crop_ratio,
                           *args, **kwargs)