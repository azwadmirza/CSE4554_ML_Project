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
        x_ = self._apply_processing(x)

        # Check if loss available
        if not hasattr(self, '_loss_grads') or self._loss_grads is None or self._output_ph is None:
            raise ValueError("Need the loss function and the labels placeholder to compute the loss gradient.")

        # Create feed_dict
        fd = {self._input_ph: x_, self._output_ph: y}
        fd.update(self._feed_dict)

        # Compute the gradient and return
        grds = self._sess.run(self._loss_grads, feed_dict=fd)
        grds = self._apply_processing_gradient(grds)
        assert grds.shape == x_.shape

        return grds