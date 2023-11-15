    def loss_gradient(self, x, y):
        """
        Compute the gradient of the loss function w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param y: Correct labels, one-vs-rest encoding.
        :type y: `np.ndarray`
        :return: Array of gradients of the same shape as `x`.
        :rtype: `np.ndarray`
        """
        from mxnet import autograd, gluon, nd

        train_mode = self._learning_phase if hasattr(self, '_learning_phase') else False

        x_ = nd.array(x, ctx=self._ctx)
        y_ = nd.array([np.argmax(y, axis=1)]).T

        x_.attach_grad()
        loss = gluon.loss.SoftmaxCrossEntropyLoss()
        with autograd.record(train_mode=train_mode):
            preds = self._model(x_)
            loss = loss(preds, y_)

        loss.backward()
        grads = x_.grad.asnumpy()
        grads = self._apply_processing_gradient(grads)
        assert grads.shape == x.shape

        return grads