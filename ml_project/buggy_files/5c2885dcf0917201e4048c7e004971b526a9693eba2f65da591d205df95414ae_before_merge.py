def label_binarize(y, classes, multilabel=False, neg_label=0, pos_label=1):
    """Binarize labels in a one-vs-all fashion

    Several regression and binary classification algorithms are
    available in the scikit. A simple way to extend these algorithms
    to the multi-class classification case is to use the so-called
    one-vs-all scheme.

    This function makes it possible to compute this transformation for a
    fixed set of class labels known ahead of time.

    Parameters
    ----------
    y : array-like
        Sequence of integer labels or multilabel data to encode.

    classes : array-like of shape [n_classes]
        Uniquely holds the label for each class.

    multilabel : boolean
        Set to true if y is encoding a multilabel tasks (with a variable
        number of label assignements per sample) rather than a multiclass task
        where one sample has one and only one label assigned.

    neg_label: int (default: 0)
        Value with which negative labels must be encoded.

    pos_label: int (default: 1)
        Value with which positive labels must be encoded.

    Returns
    -------
    Y : numpy array of shape [n_samples, n_classes]

    Examples
    --------
    >>> from sklearn.preprocessing import label_binarize
    >>> label_binarize([1, 6], classes=[1, 2, 4, 6])
    array([[1, 0, 0, 0],
           [0, 0, 0, 1]])

    The class ordering is preserved:

    >>> label_binarize([1, 6], classes=[1, 6, 4, 2])
    array([[1, 0, 0, 0],
           [0, 1, 0, 0]])

    See also
    --------
    label_binarize : function to perform the transform operation of
        LabelBinarizer with fixed classes.
    """
    y_type = type_of_target(y)

    if multilabel or len(classes) > 2:
        Y = np.zeros((len(y), len(classes)), dtype=np.int)
    else:
        Y = np.zeros((len(y), 1), dtype=np.int)

    Y += neg_label

    if multilabel:
        if y_type == "multilabel-indicator":
            Y[y == 1] = pos_label
            return Y
        elif y_type == "multilabel-sequences":
            return MultiLabelBinarizer(classes=classes).fit_transform(y)
        else:
            raise ValueError("y should be in a multilabel format, "
                             "got %r" % (y,))

    else:
        y = column_or_1d(y)

        if len(classes) == 2:
            Y[y == classes[1], 0] = pos_label
            return Y

        elif len(classes) >= 2:
            for i, k in enumerate(classes):
                Y[y == k, i] = pos_label
            return Y

        else:
            # Only one class, returns a matrix with all negative labels.
            return Y