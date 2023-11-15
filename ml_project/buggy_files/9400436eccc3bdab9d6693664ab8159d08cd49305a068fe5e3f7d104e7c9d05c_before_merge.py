def color_palette(palette=None, n_colors=None, desat=None, as_cmap=False):
    """Return a list of colors or continuous colormap defining a palette.

    Possible ``palette`` values include:
        - Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
        - Name of matplotlib colormap
        - 'husl' or 'hsl'
        - 'ch:<cubehelix arguments>'
        - 'light:<color>', 'dark:<color>', 'blend:<color>,<color>',
        - A sequence of colors in any format matplotlib accepts

    Calling this function with ``palette=None`` will return the current
    matplotlib color cycle.

    This function can also be used in a ``with`` statement to temporarily
    set the color cycle for a plot or set of plots.

    See the :ref:`tutorial <palette_tutorial>` for more information.

    Parameters
    ----------
    palette: None, string, or sequence, optional
        Name of palette or None to return current palette. If a sequence, input
        colors are used but possibly cycled and desaturated.
    n_colors : int, optional
        Number of colors in the palette. If ``None``, the default will depend
        on how ``palette`` is specified. Named palettes default to 6 colors,
        but grabbing the current palette or passing in a list of colors will
        not change the number of colors unless this is specified. Asking for
        more colors than exist in the palette will cause it to cycle. Ignored
        when ``as_cmap`` is True.
    desat : float, optional
        Proportion to desaturate each color by.
    as_cmap : bool
        If True, return a :class:`matplotlib.colors.Colormap`.

    Returns
    -------
    list of RGB tuples or :class:`matplotlib.colors.Colormap`

    See Also
    --------
    set_palette : Set the default color cycle for all plots.
    set_color_codes : Reassign color codes like ``"b"``, ``"g"``, etc. to
                      colors from one of the seaborn palettes.

    Examples
    --------

    .. include:: ../docstrings/color_palette.rst

    """
    if palette is None:
        palette = get_color_cycle()
        if n_colors is None:
            n_colors = len(palette)

    elif not isinstance(palette, str):
        palette = palette
        if n_colors is None:
            n_colors = len(palette)
    else:

        if n_colors is None:
            # Use all colors in a qualitative palette or 6 of another kind
            n_colors = QUAL_PALETTE_SIZES.get(palette, 6)

        if palette in SEABORN_PALETTES:
            # Named "seaborn variant" of matplotlib default color cycle
            palette = SEABORN_PALETTES[palette]

        elif palette == "hls":
            # Evenly spaced colors in cylindrical RGB space
            palette = hls_palette(n_colors, as_cmap=as_cmap)

        elif palette == "husl":
            # Evenly spaced colors in cylindrical Lab space
            palette = husl_palette(n_colors, as_cmap=as_cmap)

        elif palette.lower() == "jet":
            # Paternalism
            raise ValueError("No.")

        elif palette.startswith("ch:"):
            # Cubehelix palette with params specified in string
            args, kwargs = _parse_cubehelix_args(palette)
            palette = cubehelix_palette(n_colors, *args, **kwargs, as_cmap=as_cmap)

        elif palette.startswith("light:"):
            # light palette to color specified in string
            _, color = palette.split(":")
            reverse = color.endswith("_r")
            if reverse:
                color = color[:-2]
            palette = light_palette(color, n_colors, reverse=reverse, as_cmap=as_cmap)

        elif palette.startswith("dark:"):
            # light palette to color specified in string
            _, color = palette.split(":")
            reverse = color.endswith("_r")
            if reverse:
                color = color[:-2]
            palette = dark_palette(color, n_colors, reverse=reverse, as_cmap=as_cmap)

        elif palette.startswith("blend:"):
            # blend palette between colors specified in string
            _, colors = palette.split(":")
            colors = colors.split(",")
            palette = blend_palette(colors, n_colors, as_cmap=as_cmap)

        else:
            try:
                # Perhaps a named matplotlib colormap?
                palette = mpl_palette(palette, n_colors, as_cmap=as_cmap)
            except ValueError:
                raise ValueError("%s is not a valid palette name" % palette)

    if desat is not None:
        palette = [desaturate(c, desat) for c in palette]

    if not as_cmap:

        # Always return as many colors as we asked for
        pal_cycle = cycle(palette)
        palette = [next(pal_cycle) for _ in range(n_colors)]

        # Always return in r, g, b tuple format
        try:
            palette = map(mpl.colors.colorConverter.to_rgb, palette)
            palette = _ColorPalette(palette)
        except ValueError:
            raise ValueError(f"Could not generate a palette for {palette}")

    return palette