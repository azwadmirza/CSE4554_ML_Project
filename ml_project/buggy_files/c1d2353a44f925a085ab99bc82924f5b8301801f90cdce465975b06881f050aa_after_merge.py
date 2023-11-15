    def fit(self, x, y, batch_size=128, nb_epochs=10):
        """
        Fit the classifier on the training set `(x, y)`.

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
        import torch

        # Apply defences
        x_ = self._apply_processing(x)
        x_, y_ = self._apply_defences_fit(x_, y)
        y_ = np.argmax(y_, axis=1)

        num_batch = int(np.ceil(len(x_) / float(batch_size)))
        ind = np.arange(len(x_))

        # Start training
        for _ in range(nb_epochs):
            # Shuffle the examples
            random.shuffle(ind)

            # Train for one epoch
            for m in range(num_batch):
                i_batch = torch.from_numpy(x_[ind[m * batch_size:(m + 1) * batch_size]]).to(self._device)
                o_batch = torch.from_numpy(y_[ind[m * batch_size:(m + 1) * batch_size]]).to(self._device)

                # Cast to float
                i_batch = i_batch.float()

                # Zero the parameter gradients
                self._optimizer.zero_grad()

                # Actual training
                model_outputs = self._model(i_batch)
                loss = self._loss(model_outputs[-1], o_batch)
                loss.backward()
                self._optimizer.step()