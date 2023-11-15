    def fit(self, x, y, batch_size=128, nb_epochs=20):
        """
        Fit the classifier on the training set `(inputs, outputs)`.

        :param x: Training data.
        :type x: `np.ndarray`
        :param y: Labels, one-vs-rest encoding.
        :type y: `np.ndarray`
        :param batch_size: Size of batches.
        :type batch_size: `int`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        if self._optimizer is None:
            raise ValueError('An MXNet optimizer is required for fitting the model.')

        from mxnet import autograd, nd

        train_mode = self._learning_phase if hasattr(self, '_learning_phase') else True

        # Apply preprocessing and defences
        x_ = self._apply_processing(x)
        x_, y_ = self._apply_defences_fit(x_, y)
        y_ = np.argmax(y_, axis=1)

        nb_batch = int(np.ceil(len(x_) / batch_size))
        ind = np.arange(len(x_))

        for _ in range(nb_epochs):
            # Shuffle the examples
            np.random.shuffle(ind)

            # Train for one epoch
            for m in range(nb_batch):
                x_batch = nd.array(x_[ind[m * batch_size:(m + 1) * batch_size]]).as_in_context(self._ctx)
                y_batch = nd.array(y_[ind[m * batch_size:(m + 1) * batch_size]]).as_in_context(self._ctx)

                with autograd.record(train_mode=train_mode):
                    preds = self._model(x_batch)
                    loss = nd.softmax_cross_entropy(preds, y_batch)
                loss.backward()

                # Update parameters
                self._optimizer.step(batch_size)