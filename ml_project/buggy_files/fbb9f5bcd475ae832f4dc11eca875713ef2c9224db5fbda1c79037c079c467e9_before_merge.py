def resolve_inout(input=None, output=None, files=None, overwrite=False):
    """Resolves inputs and outputs from standard args and options.

    :param input: a single input filename, optional.
    :param output: a single output filename, optional.
    :param files: a sequence of filenames in which the last is the
        output filename.
    :param overwrite: whether to force overwriting the output
        file, bool.
    :return: the resolved output filename and input filenames as a
        tuple of length 2.

    If provided, the :param:`output` file may be overwritten. An output
    file extracted from :param:`files` will not be overwritten unless
    :param:`overwrite` is `True`.
    """
    resolved_output = output or (files[-1] if files else None)
    if not overwrite and resolved_output and os.path.exists(
            resolved_output):
        raise FileOverwriteError(
            "file exists and won't be overwritten without use of the "
            "`--overwrite` option.")
    resolved_inputs = (
        [input] if input else [] +
        list(files[:-1 if not output else None]) if files else [])
    return resolved_output, resolved_inputs