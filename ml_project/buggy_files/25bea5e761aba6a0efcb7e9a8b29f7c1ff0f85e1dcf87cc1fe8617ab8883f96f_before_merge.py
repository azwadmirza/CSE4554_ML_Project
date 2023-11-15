    def class_gradient(self, x, label=None, logits=False):
        """
        Compute per-class derivatives w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param label: Index of a specific per-class derivative. If an integer is provided, the gradient of that class
                      output is computed for all samples. If multiple values as provided, the first dimension should
                      match the batch size of `x`, and each value will be used as target for its corresponding sample in
                      `x`. If `None`, then gradients for all classes will be computed for each sample.
        :type label: `int` or `list`
        :param logits: `True` if the prediction should be done at the logits layer.
        :type logits: `bool`
        :return: Array of gradients of input features w.r.t. each class in the form
                 `(batch_size, nb_classes, input_shape)` when computing for all classes, otherwise shape becomes
                 `(batch_size, 1, input_shape)` when `label` parameter is specified.
        :rtype: `np.ndarray`
        """
        from mxnet import autograd, nd

        # Check value of label for computing gradients
        if not (label is None or (isinstance(label, (int, np.integer)) and label in range(self.nb_classes))
                or (isinstance(label, np.ndarray) and len(label.shape) == 1 and (label < self.nb_classes).all()
                    and label.shape[0] == x.shape[0])):
            raise ValueError('Label %s is out of range.' % str(label))

        x_ = self._apply_processing(x)
        x_ = nd.array(x_, ctx=self._ctx)
        x_.attach_grad()

        if label is None:
            with autograd.record(train_mode=False):
                if logits is True:
                    preds = self._model(x_)
                else:
                    preds = self._model(x_).softmax()
                class_slices = [preds[:, i] for i in range(self.nb_classes)]

            grads = []
            for slice_ in class_slices:
                slice_.backward(retain_graph=True)
                grad = x_.grad.asnumpy()
                grads.append(grad)
            grads = np.swapaxes(np.array(grads), 0, 1)
        elif isinstance(label, (int, np.integer)):
            with autograd.record(train_mode=False):
                if logits is True:
                    preds = self._model(x_)
                else:
                    preds = self._model(x_).softmax()
                class_slice = preds[:, label]

            class_slice.backward()
            grads = np.expand_dims(x_.grad.asnumpy(), axis=1)
        else:
            unique_labels = list(np.unique(label))

            with autograd.record(train_mode=False):
                if logits is True:
                    preds = self._model(x_)
                else:
                    preds = self._model(x_).softmax()
                class_slices = [preds[:, i] for i in unique_labels]

            grads = []
            for slice_ in class_slices:
                slice_.backward(retain_graph=True)
                grad = x_.grad.asnumpy()
                grads.append(grad)

            grads = np.swapaxes(np.array(grads), 0, 1)
            lst = [unique_labels.index(i) for i in label]
            grads = grads[np.arange(len(grads)), lst]
            grads = np.expand_dims(grads, axis=1)
            grads = self._apply_processing_gradient(grads)

        grads = self._apply_processing_gradient(grads)

        return grads