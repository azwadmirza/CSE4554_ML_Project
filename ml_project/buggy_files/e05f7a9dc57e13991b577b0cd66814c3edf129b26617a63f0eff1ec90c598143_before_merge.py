def confusion_matrix(y_true, y_pred, labels=None):
    """Compute confusion matrix to evaluate the accuracy of a classification

    By definition a confusion matrix cm is such that cm[i, j] is equal
    to the number of observations known to be in group i but predicted
    to be in group j.

    Parameters
    ----------
    y_true : array, shape = [n_samples]
        true targets

    y_pred : array, shape = [n_samples]
        estimated targets

    labels : array, shape = [n_classes]
        lists all labels occuring in the dataset.
        If none is given, those that appear at least once
        in y_true or y_pred are used.

    Returns
    -------
    CM : array, shape = [n_classes, n_classes]
        confusion matrix

    References
    ----------
    http://en.wikipedia.org/wiki/Confusion_matrix
    """
    if labels is None:
        labels = unique_labels(y_true, y_pred)
    else:
        labels = np.asarray(labels, dtype=np.int)

    n_labels = labels.size
    label_to_ind = dict((y, x) for x, y in enumerate(labels))
    # convert yt, yp into index
    y_pred = np.array([label_to_ind[x] for x in y_pred])
    y_true = np.array([label_to_ind[x] for x in y_true])

    # intersect y_pred, y_true with labels
    y_pred = y_pred[y_pred < n_labels]
    y_true = y_true[y_true < n_labels]

    CM = np.asarray(coo_matrix((np.ones(y_true.shape[0]),
                                    (y_true, y_pred)),
                               shape=(n_labels, n_labels),
                               dtype=np.int).todense())
    return CM