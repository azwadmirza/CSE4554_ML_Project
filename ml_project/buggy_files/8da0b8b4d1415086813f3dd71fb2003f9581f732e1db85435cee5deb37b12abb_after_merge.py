    def __init__(self, sess, iterator, iterator_type, iterator_arg, size, batch_size):
        """
        Create a data generator wrapper for TensorFlow. Supported iterators: initializable, reinitializable, feedable.
        :param sess: Tensorflow session.
        :type sess: `tf.Session`
        :param iterator: Data iterator from TensorFlow.
        :type iterator: `tensorflow.python.data.ops.iterator_ops.Iterator`
        :param iterator_type: Type of the iterator. Supported types: `initializable`, `reinitializable`, `feedable`.
        :type iterator_type: `string`
        :param iterator_arg: Argument to initialize the iterator. It is either a feed_dict used for the initializable
        and feedable mode, or an init_op used for the reinitializable mode.
        :type iterator_arg: `dict`, `tuple` or `tensorflow.python.framework.ops.Operation`
        :param size: Total size of the dataset.
        :type size: `int`
        :param batch_size: Size of the minibatches.
        :type batch_size: `int`
        """
        import tensorflow as tf

        super(TFDataGenerator, self).__init__(size=size, batch_size=batch_size)
        self.sess = sess
        self.iterator = iterator
        self.iterator_type = iterator_type
        self.iterator_arg = iterator_arg

        if not isinstance(iterator, tf.data.Iterator):
            raise ("Only support object tf.data.Iterator")

        if iterator_type == 'initializable':
            if type(iterator_arg) != dict:
                raise ("Need to pass a dictionary for iterator type %s" % iterator_type)
        elif iterator_type == 'reinitializable':
            if not isinstance(iterator_arg, tf.Operation):
                raise ("Need to pass a tensorflow operation for iterator type %s" % iterator_type)
        elif iterator_type == 'feedable':
            if type(iterator_arg) != tuple:
                raise ("Need to pass a tuple for iterator type %s" % iterator_type)
        else:
            raise ("Iterator type %s not supported" % iterator_type)