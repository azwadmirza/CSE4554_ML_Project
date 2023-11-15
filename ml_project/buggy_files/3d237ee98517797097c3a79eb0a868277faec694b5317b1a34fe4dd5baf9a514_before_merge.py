def _interpret_fields(fields):
    """
    Turn the fields read with load and FF2PP._extract_field into useable
    fields. One of the primary purposes of this function is to either convert
    "deferred bytes" into "deferred arrays" or "loaded bytes" into actual
    numpy arrays (via the _create_field_data) function.

    """
    land_mask = None
    landmask_compressed_fields = []
    for field in fields:
        # Store the first reference to a land mask, and use this as the
        # definitive mask for future fields in this generator.
        if land_mask is None and field.lbuser[6] == 1 and \
                (field.lbuser[3] // 1000) == 0 and \
                (field.lbuser[3] % 1000) == 30:
            land_mask = field

        # Handle land compressed data payloads,
        # when lbpack.n2 is 2.
        if (field.raw_lbpack // 10 % 10) == 2:
            if land_mask is None:
                landmask_compressed_fields.append(field)
                continue

            # Land compressed fields don't have a lbrow and lbnpt.
            field.lbrow, field.lbnpt = land_mask.lbrow, land_mask.lbnpt

        data_shape = (field.lbrow, field.lbnpt)
        _create_field_data(field, data_shape, land_mask)
        yield field

    if landmask_compressed_fields:
        if land_mask is None:
            warnings.warn('Landmask compressed fields existed without a '
                          'landmask to decompress with. The data will have '
                          'a shape of (0, 0) and will not read.')
            mask_shape = (0, 0)
        else:
            mask_shape = (land_mask.lbrow, land_mask.lbnpt)

        for field in landmask_compressed_fields:
            field.lbrow, field.lbnpt = mask_shape
            _create_field_data(field, (field.lbrow, field.lbnpt), land_mask)
            yield field