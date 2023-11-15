def label_binarize(y, classes, neg_label=0, pos_label=1,
                   sparse_output=False, multilabel=None):
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

    neg_label : int (default: 0)
        Value with which negative labels must be encoded.

    pos_label : int (default: 1)
        Value with which positive labels must be encoded.

    sparse_output : boolean (default: False),
        Set to true if output binary array is desired in CSR sparse format

    Returns
    -------
    Y : numpy array or CSR matrix of shape [n_samples, n_classes]
        Shape will be [n_samples, 1] for binary problems.

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

    Binary targets transform to a column vector

    >>> label_binarize(['yes', 'no', 'no', 'yes'], classes=['no', 'yes'])
    array([[1],
           [0],
           [0],
           [1]])

    See also
    --------
    LabelBinarizer : class used to wrap the functionality of label_binarize and
        allow for fitting to classes independently of the transform operation
    """
    if neg_label >= pos_label:
        raise ValueError("neg_label={0} must be strictly less than "
                         "pos_label={1}.".format(neg_label, pos_label))

    if (sparse_output and (pos_label == 0 or neg_label != 0)):
        raise ValueError("Sparse binarization is only supported with non "
                         "zero pos_label and zero neg_label, got "
                         "pos_label={0} and neg_label={1}"
                         "".format(pos_label, neg_label))

    if multilabel is not None:
        warnings.warn("The multilabel parameter is deprecated as of version "
                      "0.15 and will be removed in 0.17. The parameter is no "
                      "longer necessary because the value is automatically "
                      "inferred.", DeprecationWarning)

    # To account for pos_label == 0 in the dense case
    pos_switch = pos_label == 0
    if pos_switch:
        pos_label = -neg_label

    y_type = type_of_target(y)

    n_samples = y.shape[0] if sp.issparse(y) else len(y)
    n_classes = len(classes)
    classes = np.asarray(classes)

    if y_type == "binary":
        if len(classes) == 1:
            Y = np.zeros((len(y), 1), dtype=np.int)
            Y += neg_label
            return Y
        elif len(classes) >= 3:
            y_type = "multiclass"

    sorted_class = np.sort(classes)
    if (y_type == "multilabel-indicator" and classes.size != y.shape[1] or
            not set(classes).issuperset(unique_labels(y))):
        raise ValueError("classes {0} missmatch with the labels {1}"
                         "found in the data".format(classes, unique_labels(y)))

    if y_type in ("binary", "multiclass"):
        y = column_or_1d(y)
        indptr = np.arange(n_samples + 1)
        indices = np.searchsorted(sorted_class, y)
        data = np.empty_like(indices)
        data.fill(pos_label)

        Y = sp.csr_matrix((data, indices, indptr),
                          shape=(n_samples, n_classes))

    elif y_type == "multilabel-indicator":
        Y = sp.csr_matrix(y)
        if pos_label != 1:
            data = np.empty_like(Y.data)
            data.fill(pos_label)
            Y.data = data

    elif y_type == "multilabel-sequences":
        Y = MultiLabelBinarizer(classes=classes,
                                sparse_output=sparse_output).fit_transform(y)

        if sp.issparse(Y):
            Y.data[:] = pos_label
        else:
            Y[Y == 1] = pos_label
        return Y

    if not sparse_output:
        Y = Y.toarray()
        Y = astype(Y, int, copy=False)

        if neg_label != 0:
            Y[Y == 0] = neg_label

        if pos_switch:
            Y[Y == pos_label] = 0

    # preserve label ordering
    if np.any(classes != sorted_class):
        indices = np.argsort(classes)
        Y = Y[:, indices]

    if y_type == "binary":
        Y = Y[:, -1].reshape((-1, 1))

    return Y