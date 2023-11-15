def _linearly_scale(inputmatrix, inputmin, inputmax, outputmin, outputmax):
    """linearly scale input to output, used by Linke turbidity lookup"""
    inputrange = inputmax - inputmin
    outputrange = outputmax - outputmin
    delta = outputrange/inputrange  # number of indices per input unit
    inputmin = inputmin + 1.0 / delta / 2.0  # shift to center of index
    outputmax = outputmax - 1  # shift index to zero indexing
    outputmatrix = (inputmatrix - inputmin) * delta + outputmin
    err = IndexError('Input, %g, is out of range (%g, %g).' %
                     (inputmatrix, inputmax - inputrange, inputmax))
    # round down if input is within half an index or else raise index error
    if outputmatrix > outputmax:
        if np.around(outputmatrix - outputmax, 1) <= 0.5:
            outputmatrix = outputmax
        else:
            raise err
    elif outputmatrix < outputmin:
        if np.around(outputmin - outputmatrix, 1) <= 0.5:
            outputmatrix = outputmin
        else:
            raise err
    return outputmatrix