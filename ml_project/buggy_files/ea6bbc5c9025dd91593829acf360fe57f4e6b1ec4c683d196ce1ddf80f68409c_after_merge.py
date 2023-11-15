    def get_batch(self):
        """
        Provide the next batch for training in the form of a tuple `(x, y)`. The generator should loop over the data
        indefinitely.
        :return: A tuple containing a batch of data `(x, y)`.
        :rtype: `tuple`
        :raises: `ValueError` if the iterator has reached the end.
        """
        import tensorflow as tf

        # Get next batch
        next_batch = self.iterator.get_next()

        # Process to get the batch
        try:
            if self.iterator_type in ('initializable', 'reinitializable'):
                return self.sess.run(next_batch)
            else:
                return self.sess.run(next_batch, feed_dict=self.iterator_arg[1])
        except (tf.errors.FailedPreconditionError, tf.errors.OutOfRangeError):
            if self.iterator_type == 'initializable':
                self.sess.run(self.iterator.initializer, feed_dict=self.iterator_arg)
                return self.sess.run(next_batch)
            elif self.iterator_type == 'reinitializable':
                self.sess.run(self.iterator_arg)
                return self.sess.run(next_batch)
            else:
                self.sess.run(self.iterator_arg[0].initializer)
                return self.sess.run(next_batch, feed_dict=self.iterator_arg[1])