    def __init__(self, generator, size, batch_size):
        """
        Create a Keras data generator wrapper instance.

        :param generator: A generator as specified by Keras documentation. Its output must be a tuple of either
                          `(inputs, targets)` or `(inputs, targets, sample_weights)`. All arrays in this tuple must have
                          the same length. The generator is expected to loop over its data indefinitely.
        :type generator: generator function or `keras.utils.Sequence` or `keras.preprocessing.image.ImageDataGenerator`
        :param size: Total size of the dataset.
        :type size: `int` or `None`
        :param batch_size: Size of the minibatches.
        :type batch_size: `int`
        """
        self.generator = generator

        if size is not None and (type(size) is not int or size < 1):
            raise ValueError("The total size of the dataset must be an integer greater than zero.")

        self.size = size

        if type(batch_size) is not int or batch_size < 1:
            raise ValueError("The batch size must be an integer greater than zero.")

        self.batch_size = batch_size