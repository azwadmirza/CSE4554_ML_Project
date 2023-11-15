    def loss_gradient(self, x: np.ndarray, y: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute the gradient of the loss function w.r.t. `x`.

        :param x: Samples of shape (nb_samples, seq_length). Note that, it is allowable that sequences in the batch
                  could have different lengths. A possible example of `x` could be:
                  `x = np.array([np.array([0.1, 0.2, 0.1, 0.4]), np.array([0.3, 0.1])])`.
        :param y: Target values of shape (nb_samples). Each sample in `y` is a string and it may possess different
                  lengths. A possible example of `y` could be: `y = np.array(['SIXTY ONE', 'HELLO'])`.
        :return: Loss gradients of the same shape as `x`.
        """
        from warpctc_pytorch import CTCLoss

        x_ = np.array([x_i for x_i in x] + [np.array([0.1]), np.array([0.1, 0.2])])[:-2]

        # Put the model in the training mode
        self._model.train()

        # Apply preprocessing
        x_preprocessed, y_preprocessed = self._apply_preprocessing(x_, y, fit=False)

        # Transform data into the model input space
        inputs, targets, input_rates, target_sizes, batch_idx = self.transform_model_input(
            x=x_preprocessed, y=y_preprocessed, compute_gradient=True
        )

        # Compute real input sizes
        input_sizes = input_rates.mul_(inputs.size()[-1]).int()

        # Call to DeepSpeech model for prediction
        outputs, output_sizes = self._model(inputs.to(self._device), input_sizes.to(self._device))
        outputs = outputs.transpose(0, 1)
        float_outputs = outputs.float()

        # Loss function
        criterion = CTCLoss()
        loss = criterion(float_outputs, targets, output_sizes, target_sizes).to(self._device)
        loss = loss / inputs.size(0)

        # Compute gradients
        if self._use_amp:
            from apex import amp

            with amp.scale_loss(loss, self._optimizer) as scaled_loss:
                scaled_loss.backward()

        else:
            loss.backward()

        # Get results
        results = []
        for i in range(len(x_preprocessed)):
            results.append(x_preprocessed[i].grad.cpu().numpy().copy())

        results = np.array(results)

        if results.shape[0] == 1:
            results = np.array(
                [results_i for results_i in results] + [np.array([0.1]), np.array([0.1, 0.2])], dtype="object"
            )[:-2]

        results = self._apply_preprocessing_gradient(x_, results)

        if x.dtype != np.object:
            results = np.array([i for i in results], dtype=x.dtype)
            assert results.shape == x.shape and results.dtype == x.dtype

        return results