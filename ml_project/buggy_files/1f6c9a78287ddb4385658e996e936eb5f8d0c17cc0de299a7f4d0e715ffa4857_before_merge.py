    def loss_gradient(self, x, y, **kwargs):
        """
        Compute the gradient of the loss function w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param y: Target values (class labels) one-hot-encoded of shape (nb_samples, nb_classes) or indices of shape
                  (nb_samples,).
        :type y: `np.ndarray`
        :return: Array of gradients of the same shape as `x`.
        :rtype: `np.ndarray`
        """
        import mxnet as mx

        train_mode = self._learning_phase if hasattr(self, "_learning_phase") else False

        # Apply preprocessing
        x_preprocessed, y_preprocessed = self._apply_preprocessing(x, y, fit=False)

        y_preprocessed = mx.nd.array([np.argmax(y_preprocessed, axis=1)]).T
        x_preprocessed = mx.nd.array(x_preprocessed.astype(ART_NUMPY_DTYPE), ctx=self._ctx)
        x_preprocessed.attach_grad()

        with mx.autograd.record(train_mode=train_mode):
            preds = self._model(x_preprocessed)
            loss = self._loss(preds, y_preprocessed)

        loss.backward()

        # Compute gradients
        grads = x_preprocessed.grad.asnumpy()
        grads = self._apply_preprocessing_gradient(x, grads)
        assert grads.shape == x.shape

        return grads