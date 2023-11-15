def get_weights(atoms, weights):
    """Check that a `weights` argument is compatible with `atoms`.

    Parameters
    ----------
    atoms : AtomGroup or array_like
        The atoms that the `weights` should be applied to. Typically this
        is a :class:`AtomGroup` but because only the length is compared,
        any sequence for which ``len(atoms)`` is defined is acceptable.
    weights : {"mass", None} or array_like
        All MDAnalysis functions or classes understand "mass" and will then
        use ``atoms.masses``. ``None`` indicates equal weights for all atoms.
        Using an ``array_like`` assigns a custom weight to each element of
        `atoms`.

    Returns
    -------
    weights : array_like or None
         If "mass" was selected, ``atoms.masses`` is returned, otherwise the
         value of `weights` (which can be ``None``).

    Raises
    ------
    TypeError
        If `weights` is not one of the allowed values or if it is not a 1D
        array with the same length as `atoms`, then the exception is raised.
        :exc:`TypeError` is also raised if ``atoms.masses`` is not defined.
    """
    if weights == "mass":
        try:
            weights = atoms.masses
        except AttributeError:
            raise TypeError("weights='mass' selected but atoms.masses is missing")

    if iterable(weights):
        if len(weights) != len(atoms):
            raise TypeError("weights (length {0}) must be of same length as "
                            "the atoms ({1})".format(
                                len(weights), len(atoms)))
        elif len(np.asarray(weights).shape) != 1:
            raise TypeError("weights must be a 1D array, not with shape "
                            "{0}".format(np.asarray(weights).shape))
    elif weights is not None:
        raise TypeError("weights must be {'mass', None} or an iterable of the "
                        "same size as the atomgroup.")

    return weights