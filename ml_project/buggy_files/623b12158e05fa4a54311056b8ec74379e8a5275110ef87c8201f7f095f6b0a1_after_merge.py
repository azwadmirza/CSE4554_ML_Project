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
        super(KerasDataGenerator, self).__init__(size=size, batch_size=batch_size)
        self.generator = generator