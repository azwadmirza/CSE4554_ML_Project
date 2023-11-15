def resolve_inout(
    input=None, output=None, files=None, overwrite=False, num_inputs=None
):
    """Resolves inputs and outputs from standard args and options.

    Parameters
    ----------
    input : str
        A single input filename, optional.
    output : str
        A single output filename, optional.
    files : str
        A sequence of filenames in which the last is the output filename.
    overwrite : bool
        Whether to force overwriting the output file.
    num_inputs : int
        Raise exceptions if the number of resolved input files is higher
        or lower than this number.

    Returns
    -------
    tuple (str, list of str)
        The resolved output filename and input filenames as a tuple of
        length 2.

    If provided, the output file may be overwritten. An output
    file extracted from files will not be overwritten unless
    overwrite is True.

    Raises
    ------
    click.BadParameter

    """
    resolved_output = output or (files[-1] if files else None)

    if not overwrite and resolved_output and os.path.exists(resolved_output):
        raise FileOverwriteError(
            "file exists and won't be overwritten without use of the `--overwrite` option."
        )

    resolved_inputs = (
        [input] if input else [] +
        list(files[:-1 if not output else None]) if files else [])

    if num_inputs is not None:
        if len(resolved_inputs) < num_inputs:
            raise click.BadParameter("Insufficient inputs")
        elif len(resolved_inputs) > num_inputs:
            raise click.BadParameter("Too many inputs")

    return resolved_output, resolved_inputs