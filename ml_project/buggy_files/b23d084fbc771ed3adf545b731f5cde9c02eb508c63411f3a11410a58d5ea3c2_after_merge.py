    def fit_generator(self, generator, nb_epochs=20):
        """
        Fit the classifier using the generator that yields batches as specified.

        :param generator: Batch generator providing `(x, y)` for each epoch. If the generator can be used for native
                          training in TensorFlow, it will.
        :type generator: `DataGenerator`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        from art.data_generators import TFDataGenerator

        # Train directly in Tensorflow
        if isinstance(generator, TFDataGenerator) and not (hasattr(
                self, 'label_smooth') or hasattr(self, 'feature_squeeze')):
            for _ in range(nb_epochs):
                for _ in range(int(generator.size / generator.batch_size)):
                    i_batch, o_batch = generator.get_batch()

                    # Create feed_dict
                    fd = {self._input_ph: i_batch, self._output_ph: o_batch}
                    fd.update(self._feed_dict)

                    # Run train step
                    self._sess.run(self._train, feed_dict=fd)
        else:
            super(TFClassifier, self).fit_generator(generator, nb_epochs=nb_epochs)