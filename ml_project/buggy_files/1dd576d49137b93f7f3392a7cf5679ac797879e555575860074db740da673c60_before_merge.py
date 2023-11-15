def to_rgba_array(c, alpha=None):
    """Convert *c* to a (n, 4) array of RGBA colors.

    If *alpha* is not ``None``, it forces the alpha value.  If *c* is
    ``"none"`` (case-insensitive) or an empty list, an empty array is returned.
    """
    # Special-case inputs that are already arrays, for performance.  (If the
    # array has the wrong kind or shape, raise the error during one-at-a-time
    # conversion.)
    if (isinstance(c, np.ndarray) and c.dtype.kind in "if"
            and c.ndim == 2 and c.shape[1] in [3, 4]):
        if c.shape[1] == 3:
            result = np.column_stack([c, np.zeros(len(c))])
            result[:, -1] = alpha if alpha is not None else 1.
        elif c.shape[1] == 4:
            result = c.copy()
            if alpha is not None:
                result[:, -1] = alpha
        if np.any((result < 0) | (result > 1)):
            raise ValueError("RGBA values should be within 0-1 range")
        return result
    # Handle single values.
    # Note that this occurs *after* handling inputs that are already arrays, as
    # `to_rgba(c, alpha)` (below) is expensive for such inputs, due to the need
    # to format the array in the ValueError message(!).
    if cbook._str_lower_equal(c, "none"):
        return np.zeros((0, 4), float)
    try:
        return np.array([to_rgba(c, alpha)], float)
    except (ValueError, TypeError):
        pass

    # Convert one at a time.
    if isinstance(c, str):
        # Single string as color sequence.
        # This is deprecated and will be removed in the future.
        try:
            result = np.array([to_rgba(cc, alpha) for cc in c])
        except ValueError:
            raise ValueError(
                "'%s' is neither a valid single color nor a color sequence "
                "consisting of single character color specifiers such as "
                "'rgb'. Note also that the latter is deprecated." % c)
        else:
            cbook.warn_deprecated("3.2", message="Using a string of single "
                                  "character colors as a color sequence is "
                                  "deprecated. Use an explicit list instead.")
    else:
        result = np.array([to_rgba(cc, alpha) for cc in c])

    return result