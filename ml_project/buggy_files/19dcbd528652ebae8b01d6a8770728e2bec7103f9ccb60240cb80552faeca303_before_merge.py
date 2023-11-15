def pinball_loss(
    y_true: TensorLike, y_pred: TensorLike, tau: FloatTensorLike = 0.5
) -> tf.Tensor:
    """Computes the pinball loss between `y_true` and `y_pred`.

    `loss = maximum(tau * (y_true - y_pred), (tau - 1) * (y_true - y_pred))`

    In the context of regression this, loss yields an estimator of the tau
    conditional quantile.

    See: https://en.wikipedia.org/wiki/Quantile_regression

    Usage:
    ```python
    loss = pinball_loss([0., 0., 1., 1.], [1., 1., 1., 0.], tau=.1)

    # loss = max(0.1 * (y_true - y_pred), (0.1 - 1) * (y_true - y_pred))
    #      = (0.9 + 0.9 + 0 + 0.1) / 4

    print('Loss: ', loss.numpy())  # Loss: 0.475
    ```

    Args:
      y_true: Ground truth values. shape = `[batch_size, d0, .. dN]`
      y_pred: The predicted values. shape = `[batch_size, d0, .. dN]`
      tau: (Optional) Float in [0, 1] or a tensor taking values in [0, 1] and
        shape = `[d0,..., dn]`.  It defines the slope of the pinball loss. In
        the context of quantile regression, the value of tau determines the
        conditional quantile level. When tau = 0.5, this amounts to l1
        regression, an estimator of the conditional median (0.5 quantile).

    Returns:
        pinball_loss: 1-D float `Tensor` with shape [batch_size].

    References:
      - https://en.wikipedia.org/wiki/Quantile_regression
      - https://projecteuclid.org/download/pdfview_1/euclid.bj/1297173840
    """
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.cast(y_true, y_pred.dtype)

    # broadcast the pinball slope along the batch dimension, and clip to
    # acceptable values
    tau = tf.expand_dims(tf.cast(tau, y_pred.dtype), 0)
    one = tf.cast(1, tau.dtype)

    delta_y = y_true - y_pred
    pinball = tf.math.maximum(tau * delta_y, (tau - one) * delta_y)
    return tf.reduce_mean(tf.keras.backend.batch_flatten(pinball), axis=-1)