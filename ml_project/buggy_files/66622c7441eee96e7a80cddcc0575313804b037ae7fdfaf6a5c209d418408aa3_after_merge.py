def save_fields(fields, target, append=False):
    """
    Save an iterable of PP fields to a PP file.

    Args:

    * fields:
        An iterable of PP fields.
    * target:
        A filename or open file handle.

    Kwargs:

    * append:
        Whether to start a new file afresh or add the cube(s) to the end
        of the file.
        Only applicable when target is a filename, not a file handle.
        Default is False.

    See also :func:`iris.io.save`.

    """
    # Open issues

    # Deal with:
    #   LBLREC - Length of data record in words (incl. extra data)
    #       Done on save(*)
    #   LBUSER[0] - Data type
    #       Done on save(*)
    #   LBUSER[1] - Start address in DATA (?! or just set to "null"?)
    #   BLEV - Level - the value of the coordinate for LBVC

    # *) With the current on-save way of handling LBLREC and LBUSER[0] we can't
    # check if they've been set correctly without *actually* saving as a binary
    # PP file. That also means you can't use the same reference.txt file for
    # loaded vs saved fields (unless you re-load the saved field!).

    # Set to (or leave as) "null":
    #   LBEGIN - Address of start of field in direct access dataset
    #   LBEXP - Experiment identification
    #   LBPROJ - Fields file projection number
    #   LBTYP - Fields file field type code
    #   LBLEV - Fields file level code / hybrid height model level

    if isinstance(target, six.string_types):
        pp_file = open(target, "ab" if append else "wb")
    elif hasattr(target, "write"):
        if hasattr(target, "mode") and "b" not in target.mode:
            raise ValueError("Target not binary")
        pp_file = target
    else:
        raise ValueError("Can only save pp to filename or writable")

    try:
        # Save each field
        for pp_field in fields:
            # Write to file
            pp_field.save(pp_file)
    finally:
        if isinstance(target, six.string_types):
            pp_file.close()