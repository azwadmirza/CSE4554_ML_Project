    def fit_generator(self, generator, nb_epochs=20):
        """
        Fit the classifier using the generator that yields batches as specified.

        :param generator: Batch generator providing `(x, y)` for each epoch. If the generator can be used for native
                          training in Keras, it will.
        :type generator: `DataGenerator`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        from art.data_generators import KerasDataGenerator

        # Try to use the generator as a Keras native generator, otherwise use it through the `DataGenerator` interface
        # TODO Testing for preprocessing defenses is currently hardcoded; this should be improved (add property)
        if isinstance(generator, KerasDataGenerator) and \
                not (hasattr(self, 'label_smooth') or hasattr(self, 'feature_squeeze')):
            try:
                self._model.fit_generator(generator.generator, epochs=nb_epochs)
            except ValueError:
                logger.info('Unable to use data generator as Keras generator. Now treating as framework-independent.')
                super(KerasClassifier, self).fit_generator(generator, nb_epochs=nb_epochs)
        else:
            super(KerasClassifier, self).fit_generator(generator, nb_epochs=nb_epochs)