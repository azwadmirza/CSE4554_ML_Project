    def fit_generator(self, generator, nb_epochs=20):
        """
        Fit the classifier using the generator that yields batches as specified.

        :param generator: Batch generator providing `(x, y)` for each epoch.
        :type generator: `DataGenerator`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        from mxnet import autograd, nd
        from art.data_generators import MXDataGenerator

        if isinstance(generator, MXDataGenerator) and \
                not (hasattr(self, 'label_smooth') or hasattr(self, 'feature_squeeze')):
            # Train directly in MXNet
            for _ in range(nb_epochs):
                for x_batch, y_batch in generator.data_loader:
                    x_batch = nd.array(x_batch).as_in_context(self._ctx)
                    y_batch = np.argmax(y_batch, axis=1)
                    y_batch = nd.array(y_batch).as_in_context(self._ctx)

                    with autograd.record(train_mode=True):
                        preds = self._model(x_batch)
                        loss = nd.softmax_cross_entropy(preds, y_batch)
                    loss.backward()

                    # Update parameters
                    self._optimizer.step(x_batch.shape[0])
        else:
            # Fit a generic data generator through the API
            super(MXClassifier, self).fit_generator(generator, nb_epochs=nb_epochs)