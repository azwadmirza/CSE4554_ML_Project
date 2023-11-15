def to_rgba(c, alpha=None):
    """
    Convert *c* to an RGBA color.

    Parameters
    ----------
    c : Matplotlib color

    alpha : scalar, optional
        If *alpha* is not ``None``, it forces the alpha value, except if *c* is
        ``"none"`` (case-insensitive), which always maps to ``(0, 0, 0, 0)``.

    Returns
    -------
    tuple
        Tuple of ``(r, g, b, a)`` scalars.
    """
    # Special-case nth color syntax because it should not be cached.
    if _is_nth_color(c):
        from matplotlib import rcParams
        prop_cycler = rcParams['axes.prop_cycle']
        colors = prop_cycler.by_key().get('color', ['k'])
        c = colors[int(c[1:]) % len(colors)]
    try:
        rgba = _colors_full_map.cache[c, alpha]
    except (KeyError, TypeError):  # Not in cache, or unhashable.
        rgba = None
    if rgba is None:  # Suppress exception chaining of cache lookup failure.
        rgba = _to_rgba_no_colorcycle(c, alpha)
        try:
            _colors_full_map.cache[c, alpha] = rgba
        except TypeError:
            pass
    return rgba