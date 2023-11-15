    def predict(self, x, logits=False, batch_size=128):
        """
        Perform prediction for a batch of inputs.

        :param x: Test set.
        :type x: `np.ndarray`
        :param logits: `True` if the prediction should be done at the logits layer.
        :type logits: `bool`
        :param batch_size: Size of batches.
        :type batch_size: `int`
        :return: Array of predictions of shape `(nb_inputs, self.nb_classes)`.
        :rtype: `np.ndarray`
        """
        from mxnet import autograd, nd

        train_mode = self._learning_phase if hasattr(self, '_learning_phase') else False

        # Apply preprocessing and defences
        x_ = self._apply_processing(x)
        x_ = self._apply_defences_predict(x_)

        # Run prediction with batch processing
        results = np.zeros((x_.shape[0], self.nb_classes), dtype=np.float32)
        num_batch = int(np.ceil(len(x_) / float(batch_size)))
        for m in range(num_batch):
            # Batch indexes
            begin, end = m * batch_size, min((m + 1) * batch_size, x_.shape[0])

            # Predict
            x_batch = nd.array(x_[begin:end], ctx=self._ctx)
            x_batch.attach_grad()
            with autograd.record(train_mode=train_mode):
                preds = self._model(x_batch)

            if logits is False:
                preds = preds.softmax()

            results[begin:end] = preds.asnumpy()

        return results