    def fit_generator(self, generator, nb_epochs=20):
        """
        Fit the classifier using the generator that yields batches as specified.

        :param generator: Batch generator providing `(x, y)` for each epoch.
        :type generator: `DataGenerator`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        import torch
        from art.data_generators import PyTorchDataGenerator

        # Train directly in PyTorch
        if isinstance(generator, PyTorchDataGenerator) and \
                not (hasattr(self, 'label_smooth') or hasattr(self, 'feature_squeeze')):
            for _ in range(nb_epochs):
                # Set train phase
                self._model.train(True)

                for i_batch, o_batch in generator.data_loader:
                    if isinstance(i_batch, np.ndarray):
                        i_batch = torch.from_numpy(i_batch).to(self._device).float()
                    else:
                        i_batch = i_batch.to(self._device).float()

                    if isinstance(o_batch, np.ndarray):
                        o_batch = torch.argmax(torch.from_numpy(o_batch).to(self._device), dim=1)
                    else:
                        o_batch = torch.argmax(o_batch.to(self._device), dim=1)

                    # Zero the parameter gradients
                    self._optimizer.zero_grad()

                    # Actual training
                    model_outputs = self._model(i_batch)
                    loss = self._loss(model_outputs[-1], o_batch)
                    loss.backward()
                    self._optimizer.step()
        else:
            # Fit a generic data generator through the API
            super(PyTorchClassifier, self).fit_generator(generator, nb_epochs=nb_epochs)