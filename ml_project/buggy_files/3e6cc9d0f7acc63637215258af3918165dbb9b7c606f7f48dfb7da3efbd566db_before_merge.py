def binary_repr(num, width=None):
    """
    Return the binary representation of the input number as a string.

    For negative numbers, if width is not given, a minus sign is added to the
    front. If width is given, the two's complement of the number is
    returned, with respect to that width.

    In a two's-complement system negative numbers are represented by the two's
    complement of the absolute value. This is the most common method of
    representing signed integers on computers [1]_. A N-bit two's-complement
    system can represent every integer in the range
    :math:`-2^{N-1}` to :math:`+2^{N-1}-1`.

    Parameters
    ----------
    num : int
        Only an integer decimal number can be used.
    width : int, optional
        The length of the returned string if `num` is positive, or the length
        of the two's complement if `num` is negative, provided that `width` is
        at least a sufficient number of bits for `num` to be represented in the
        designated form.

        If the `width` value is insufficient, it will be ignored, and `num` will
        be returned in binary (`num` > 0) or two's complement (`num` < 0) form
        with its width equal to the minimum number of bits needed to represent
        the number in the designated form. This behavior is deprecated and will
        later raise an error.

        .. deprecated:: 1.12.0

    Returns
    -------
    bin : str
        Binary representation of `num` or two's complement of `num`.

    See Also
    --------
    base_repr: Return a string representation of a number in the given base
               system.
    bin: Python's built-in binary representation generator of an integer.

    Notes
    -----
    `binary_repr` is equivalent to using `base_repr` with base 2, but about 25x
    faster.

    References
    ----------
    .. [1] Wikipedia, "Two's complement",
        https://en.wikipedia.org/wiki/Two's_complement

    Examples
    --------
    >>> np.binary_repr(3)
    '11'
    >>> np.binary_repr(-3)
    '-11'
    >>> np.binary_repr(3, width=4)
    '0011'

    The two's complement is returned when the input number is negative and
    width is specified:

    >>> np.binary_repr(-3, width=3)
    '101'
    >>> np.binary_repr(-3, width=5)
    '11101'

    """
    def warn_if_insufficient(width, binwidth):
        if width is not None and width < binwidth:
            warnings.warn(
                "Insufficient bit width provided. This behavior "
                "will raise an error in the future.", DeprecationWarning,
                stacklevel=3)

    if num == 0:
        return '0' * (width or 1)

    elif num > 0:
        binary = bin(num)[2:]
        binwidth = len(binary)
        outwidth = (binwidth if width is None
                    else max(binwidth, width))
        warn_if_insufficient(width, binwidth)
        return binary.zfill(outwidth)

    else:
        if width is None:
            return '-' + bin(-num)[2:]

        else:
            poswidth = len(bin(-num)[2:])

            # See gh-8679: remove extra digit
            # for numbers at boundaries.
            if 2**(poswidth - 1) == -num:
                poswidth -= 1

            twocomp = 2**(poswidth + 1) + num
            binary = bin(twocomp)[2:]
            binwidth = len(binary)

            outwidth = max(binwidth, width)
            warn_if_insufficient(width, binwidth)
            return '1' * (outwidth - binwidth) + binary