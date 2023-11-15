def _to_rgba_no_colorcycle(c, alpha=None):
    """Convert *c* to an RGBA color, with no support for color-cycle syntax.

    If *alpha* is not ``None``, it forces the alpha value, except if *c* is
    ``"none"`` (case-insensitive), which always maps to ``(0, 0, 0, 0)``.
    """
    orig_c = c
    if c is np.ma.masked:
        return (0., 0., 0., 0.)
    if isinstance(c, str):
        if c.lower() == "none":
            return (0., 0., 0., 0.)
        # Named color.
        try:
            # This may turn c into a non-string, so we check again below.
            c = _colors_full_map[c]
        except KeyError:
            try:
                c = _colors_full_map[c.lower()]
            except KeyError:
                pass
            else:
                if len(orig_c) == 1:
                    cbook.warn_deprecated(
                        "3.1", message="Support for uppercase "
                        "single-letter colors is deprecated since Matplotlib "
                        "%(since)s and will be removed %(removal)s; please "
                        "use lowercase instead.")
    if isinstance(c, str):
        # hex color with no alpha.
        match = re.match(r"\A#[a-fA-F0-9]{6}\Z", c)
        if match:
            return (tuple(int(n, 16) / 255
                          for n in [c[1:3], c[3:5], c[5:7]])
                    + (alpha if alpha is not None else 1.,))
        # hex color with alpha.
        match = re.match(r"\A#[a-fA-F0-9]{8}\Z", c)
        if match:
            color = [int(n, 16) / 255
                     for n in [c[1:3], c[3:5], c[5:7], c[7:9]]]
            if alpha is not None:
                color[-1] = alpha
            return tuple(color)
        # string gray.
        try:
            c = float(c)
        except ValueError:
            pass
        else:
            if not (0 <= c <= 1):
                raise ValueError(
                    f"Invalid string grayscale value {orig_c!r}. "
                    f"Value must be within 0-1 range")
            return c, c, c, alpha if alpha is not None else 1.
        raise ValueError(f"Invalid RGBA argument: {orig_c!r}")
    # tuple color.
    c = np.array(c)
    if not np.can_cast(c.dtype, float, "same_kind") or c.ndim != 1:
        # Test the dtype explicitly as `map(float, ...)`, `np.array(...,
        # float)` and `np.array(...).astype(float)` all convert "0.5" to 0.5.
        # Test dimensionality to reject single floats.
        raise ValueError(f"Invalid RGBA argument: {orig_c!r}")
    # Return a tuple to prevent the cached value from being modified.
    c = tuple(c.astype(float))
    if len(c) not in [3, 4]:
        raise ValueError("RGBA sequence should have length 3 or 4")
    if len(c) == 3 and alpha is None:
        alpha = 1
    if alpha is not None:
        c = c[:3] + (alpha,)
    if any(elem < 0 or elem > 1 for elem in c):
        raise ValueError("RGBA values should be within 0-1 range")
    return c