def color_gradient(
    size,
    p1,
    p2=None,
    vector=None,
    radius=None,
    color_1=0.0,
    color_2=1.0,
    shape="linear",
    offset=0,
):
    """Draw a linear, bilinear, or radial gradient.

    The result is a picture of size ``size``, whose color varies
    gradually from color `color_1` in position ``p1`` to color ``color_2``
    in position ``p2``.

    If it is a RGB picture the result must be transformed into
    a 'uint8' array to be displayed normally:


    Parameters
    ------------

    size
        Size (width, height) in pixels of the final picture/array.

    p1, p2
        Coordinates (x,y) in pixels of the limit point for ``color_1``
        and ``color_2``. The color 'before' ``p1`` is ``color_1`` and it
        gradually changes in the direction of ``p2`` until it is ``color_2``
        when it reaches ``p2``.

    vector
        A vector [x,y] in pixels that can be provided instead of ``p2``.
        ``p2`` is then defined as (p1 + vector).

    color_1, color_2
        Either floats between 0 and 1 (for gradients used in masks)
        or [R,G,B] arrays (for colored gradients).

    shape
        'linear', 'bilinear', or 'circular'.
        In a linear gradient the color varies in one direction,
        from point ``p1`` to point ``p2``.
        In a bilinear gradient it also varies symetrically from ``p1``
        in the other direction.
        In a circular gradient it goes from ``color_1`` to ``color_2`` in all
        directions.

    offset
        Real number between 0 and 1 indicating the fraction of the vector
        at which the gradient actually starts. For instance if ``offset``
        is 0.9 in a gradient going from p1 to p2, then the gradient will
        only occur near p2 (before that everything is of color ``color_1``)
        If the offset is 0.9 in a radial gradient, the gradient will
        occur in the region located between 90% and 100% of the radius,
        this creates a blurry disc of radius d(p1,p2).

    Returns
    --------

    image
        An Numpy array of dimensions (W,H,ncolors) of type float
        representing the image of the gradient.


    Examples
    ---------

    >>> grad = color_gradient(blabla).astype('uint8')

    """

    # np-arrayize and change x,y coordinates to y,x
    w, h = size

    color_1 = np.array(color_1).astype(float)
    color_2 = np.array(color_2).astype(float)

    if shape == "bilinear":
        if vector is None:
            if p2 is None:
                raise ValueError("You must provide either 'p2' or 'vector'")
            vector = np.array(p2) - np.array(p1)

        m1, m2 = [
            color_gradient(
                size,
                p1,
                vector=v,
                color_1=1.0,
                color_2=0.0,
                shape="linear",
                offset=offset,
            )
            for v in [vector, -vector]
        ]

        arr = np.maximum(m1, m2)
        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return arr * color_1 + (1 - arr) * color_2

    p1 = np.array(p1[::-1]).astype(float)

    M = np.dstack(np.meshgrid(range(w), range(h))[::-1]).astype(float)

    if shape == "linear":
        if vector is None:
            if p2 is not None:
                vector = np.array(p2[::-1]) - p1
            else:
                raise ValueError("You must provide either 'p2' or 'vector'")
        else:
            vector = np.array(vector[::-1])

        norm = np.linalg.norm(vector)
        n_vec = vector / norm ** 2  # norm 1/norm(vector)

        p1 = p1 + offset * vector
        arr = (M - p1).dot(n_vec) / (1 - offset)
        arr = np.minimum(1, np.maximum(0, arr))
        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return arr * color_1 + (1 - arr) * color_2

    elif shape == "radial":
        if (radius or 0) == 0:
            arr = np.ones((h, w))
        else:
            arr = (np.sqrt(((M - p1) ** 2).sum(axis=2))) - offset * radius
            arr = arr / ((1 - offset) * radius)
            arr = np.minimum(1.0, np.maximum(0, arr))

        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return (1 - arr) * color_1 + arr * color_2
    raise ValueError("Invalid shape, should be either 'radial', 'linear' or 'bilinear'")