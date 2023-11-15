def is_sequence_of_sequences(y):
    """ Check if ``y`` is in the sequence of sequences format (multilabel).

    This format is DEPRECATED.

    Parameters
    ----------
    y : sequence or array.

    Returns
    -------
    out : bool,
        Return ``True``, if ``y`` is a sequence of sequences else ``False``.
    """
    # the explicit check for ndarray is for forward compatibility; future
    # versions of Numpy might want to register ndarray as a Sequence
    try:
        out = (not isinstance(y[0], np.ndarray) and isinstance(y[0], Sequence)
               and not isinstance(y[0], string_types))
    except IndexError:
        return False
    if out:
        warnings.warn('Direct support for sequence of sequences multilabel '
                      'representation will be unavailable from version 0.17. '
                      'Use sklearn.preprocessing.MultiLabelBinarizer to '
                      'convert to a label indicator representation.',
                      DeprecationWarning)
    return out