def _linearly_scale(inputmatrix, inputmin, inputmax, outputmin, outputmax):
    """ used by linke turbidity lookup function """

    inputrange = inputmax - inputmin
    outputrange = outputmax - outputmin
    outputmatrix = (inputmatrix-inputmin) * outputrange/inputrange + outputmin
    return outputmatrix