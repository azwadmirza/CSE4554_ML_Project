def log_loss(y_true, y_pred, eps=1e-15, normalize=True):
    """Log loss, aka logistic loss or cross-entropy loss.

    This is the loss function used in (multinomial) logistic regression
    and extensions of it such as neural networks, defined as the negative
    log-likelihood of the true labels given a probabilistic classifier's
    predictions. For a single sample with true label yt in {0,1} and
    estimated probability yp that yt = 1, the log loss is

        -log P(yt|yp) = -(yt log(yp) + (1 - yt) log(1 - yp))

    Parameters
    ----------
    y_true : array-like or label indicator matrix
        Ground truth (correct) labels for n_samples samples.

    y_pred : array-like of float, shape = (n_samples, n_classes)
        Predicted probabilities, as returned by a classifier's
        predict_proba method.

    eps : float
        Log loss is undefined for p=0 or p=1, so probabilities are
        clipped to max(eps, min(1 - eps, p)).

    normalize : bool, optional (default=True)
        If true, return the mean loss per sample.
        Otherwise, return the total loss.

    Returns
    -------
    loss : float

    Examples
    --------
    >>> log_loss(["spam", "ham", "ham", "spam"],  # doctest: +ELLIPSIS
    ...          [[.1, .9], [.9, .1], [.8, .2], [.35, .65]])
    0.21616...

    References
    ----------
    C.M. Bishop (2006). Pattern Recognition and Machine Learning. Springer,
    p. 209.

    Notes
    -----
    The logarithm used is the natural logarithm (base-e).
    """
    lb = LabelBinarizer()
    T = lb.fit_transform(y_true)
    if T.shape[1] == 1:
        T = np.append(1 - T, T, axis=1)

    # Clipping
    Y = np.clip(y_pred, eps, 1 - eps)

    # This happens in cases when elements in y_pred have type "str".
    if not isinstance(Y, np.ndarray):
        raise ValueError("y_pred should be an array of floats.")

    # If y_pred is of single dimension, assume y_true to be binary
    # and then check.
    if Y.ndim == 1:
        Y = Y[:, np.newaxis]
    if Y.shape[1] == 1:
        Y = np.append(1 - Y, Y, axis=1)

    # Check if dimensions are consistent.
    T, Y = check_arrays(T, Y)
    if T.shape[1] != Y.shape[1]:
        raise ValueError("y_true and y_pred have different number of classes "
                         "%d, %d" % (T.shape[1], Y.shape[1]))

    # Renormalize
    Y /= Y.sum(axis=1)[:, np.newaxis]
    loss = -(T * np.log(Y)).sum()
    return loss / T.shape[0] if normalize else loss