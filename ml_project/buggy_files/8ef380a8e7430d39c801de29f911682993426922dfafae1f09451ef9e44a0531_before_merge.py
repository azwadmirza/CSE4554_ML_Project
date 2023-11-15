    def Dataset(*args, **kwargs):
        """Dataset for AutoGluon image classification tasks. 
           May either be a :class:`autogluon.task.image_classification.ImageFolderDataset`, :class:`autogluon.task.image_classification.RecordDataset`, 
           or a popular dataset already built into AutoGluon ('mnist', 'fashionmnist', 'cifar10', 'cifar100', 'imagenet').

        Parameters
        ----------
        name : str, optional
            Which built-in dataset to use, will override all other options if specified.
            The options are: 'mnist', 'fashionmnist', 'cifar', 'cifar10', 'cifar100', 'imagenet'
        train : bool, default = True
            Whether this dataset should be used for training or validation.
        train_path : str
            The training data location. If using :class:`ImageFolderDataset`,
            image folder`path/to/the/folder` should be provided. 
            If using :class:`RecordDataset`, the `path/to/*.rec` should be provided.
        input_size : int
            The input image size.
        crop_ratio : float
            Center crop ratio (for evaluation only).
        
        Returns
        -------
        Dataset object that can be passed to `task.fit()`, which is actually an :class:`autogluon.space.AutoGluonObject`. 
        To interact with such an object yourself, you must first call `Dataset.init()` to instantiate the object in Python.
        """
        return get_dataset(*args, **kwargs)