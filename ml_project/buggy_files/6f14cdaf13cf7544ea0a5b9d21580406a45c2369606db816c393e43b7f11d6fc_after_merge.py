def apply_color_lut(arr, ds=None, palette=None):
    """Apply a color palette lookup table to `arr`.

    .. versionadded:: 1.4

    If (0028,1201-1203) *Palette Color Lookup Table Data* are missing
    then (0028,1221-1223) *Segmented Palette Color Lookup Table Data* must be
    present and vice versa. The presence of (0028,1204) *Alpha Palette Color
    Lookup Table Data* or (0028,1224) *Alpha Segmented Palette Color Lookup
    Table Data* is optional.

    Use of this function with the :dcm:`Enhanced Palette Color Lookup Table
    Module<part03/sect_C.7.6.23.html>` or :dcm:`Supplemental Palette Color LUT
    Module<part03/sect_C.7.6.19.html>` is not currently supported.

    Parameters
    ----------
    arr : numpy.ndarray
        The pixel data to apply the color palette to.
    ds : dataset.Dataset, optional
        Required if `palette` is not supplied. A
        :class:`~pydicom.dataset.Dataset` containing a suitable
        :dcm:`Image Pixel<part03/sect_C.7.6.3.html>` or
        :dcm:`Palette Color Lookup Table<part03/sect_C.7.9.html>` Module.
    palette : str or uid.UID, optional
        Required if `ds` is not supplied. The name of one of the
        :dcm:`well-known<part06/chapter_B.html>` color palettes defined by the
        DICOM Standard. One of: ``'HOT_IRON'``, ``'PET'``,
        ``'HOT_METAL_BLUE'``, ``'PET_20_STEP'``, ``'SPRING'``, ``'SUMMER'``,
        ``'FALL'``, ``'WINTER'`` or the corresponding well-known (0008,0018)
        *SOP Instance UID*.

    Returns
    -------
    numpy.ndarray
        The RGB or RGBA pixel data as an array of ``np.uint8`` or ``np.uint16``
        values, depending on the 3rd value of (0028,1201) *Red Palette Color
        Lookup Table Descriptor*.

    References
    ----------

    * :dcm:`Image Pixel Module<part03/sect_C.7.6.3.html>`
    * :dcm:`Supplemental Palette Color LUT Module<part03/sect_C.7.6.19.html>`
    * :dcm:`Enhanced Palette Color LUT Module<part03/sect_C.7.6.23.html>`
    * :dcm:`Palette Colour LUT Module<part03/sect_C.7.9.html>`
    * :dcm:`Supplemental Palette Color LUTs
      <part03/sect_C.8.16.2.html#sect_C.8.16.2.1.1.1>`
    """
    # Note: input value (IV) is the stored pixel value in `arr`
    # LUTs[IV] -> [R, G, B] values at the IV pixel location in `arr`
    if not ds and not palette:
        raise ValueError("Either 'ds' or 'palette' is required")

    if palette:
        # Well-known palettes are all 8-bits per entry
        datasets = {
            '1.2.840.10008.1.5.1': 'hotiron.dcm',
            '1.2.840.10008.1.5.2': 'pet.dcm',
            '1.2.840.10008.1.5.3': 'hotmetalblue.dcm',
            '1.2.840.10008.1.5.4': 'pet20step.dcm',
            '1.2.840.10008.1.5.5': 'spring.dcm',
            '1.2.840.10008.1.5.6': 'summer.dcm',
            '1.2.840.10008.1.5.7': 'fall.dcm',
            '1.2.840.10008.1.5.8': 'winter.dcm',
        }
        if not UID(palette).is_valid:
            try:
                uids = {
                    'HOT_IRON': '1.2.840.10008.1.5.1',
                    'PET': '1.2.840.10008.1.5.2',
                    'HOT_METAL_BLUE': '1.2.840.10008.1.5.3',
                    'PET_20_STEP': '1.2.840.10008.1.5.4',
                    'SPRING': '1.2.840.10008.1.5.5',
                    'SUMMER': '1.2.840.10008.1.5.6',
                    'FALL': '1.2.840.10008.1.5.8',
                    'WINTER': '1.2.840.10008.1.5.7',
                }
                palette = uids[palette]
            except KeyError:
                raise ValueError("Unknown palette '{}'".format(palette))

        try:
            from pydicom import dcmread
            fname = datasets[palette]
            ds = dcmread(get_palette_files(fname)[0])
        except KeyError:
            raise ValueError("Unknown palette '{}'".format(palette))

    # C.8.16.2.1.1.1: Supplemental Palette Color LUT
    # TODO: Requires greyscale visualisation pipeline
    if getattr(ds, 'PixelPresentation', None) in ['MIXED', 'COLOR']:
        raise ValueError(
            "Use of this function with the Supplemental Palette Color Lookup "
            "Table Module is not currently supported"
        )

    if 'RedPaletteColorLookupTableDescriptor' not in ds:
        raise ValueError("No suitable Palette Color Lookup Table Module found")

    # All channels are supposed to be identical
    lut_desc = ds.RedPaletteColorLookupTableDescriptor
    # A value of 0 = 2^16 entries
    nr_entries = lut_desc[0] or 2**16

    # May be negative if Pixel Representation is 1
    first_map = lut_desc[1]
    # Actual bit depth may be larger (8 bit entries in 16 bits allocated)
    nominal_depth = lut_desc[2]
    dtype = np.dtype('uint{:.0f}'.format(nominal_depth))

    luts = []
    if 'RedPaletteColorLookupTableData' in ds:
        # LUT Data is described by PS3.3, C.7.6.3.1.6
        r_lut = ds.RedPaletteColorLookupTableData
        g_lut = ds.GreenPaletteColorLookupTableData
        b_lut = ds.BluePaletteColorLookupTableData
        a_lut = getattr(ds, 'AlphaPaletteColorLookupTableData', None)

        actual_depth = len(r_lut) / nr_entries * 8
        dtype = np.dtype('uint{:.0f}'.format(actual_depth))

        for lut in [ii for ii in [r_lut, g_lut, b_lut, a_lut] if ii]:
            luts.append(np.frombuffer(lut, dtype=dtype))
    elif 'SegmentedRedPaletteColorLookupTableData' in ds:
        # Segmented LUT Data is described by PS3.3, C.7.9.2
        r_lut = ds.SegmentedRedPaletteColorLookupTableData
        g_lut = ds.SegmentedGreenPaletteColorLookupTableData
        b_lut = ds.SegmentedBluePaletteColorLookupTableData
        a_lut = getattr(ds, 'SegmentedAlphaPaletteColorLookupTableData', None)

        endianness = '<' if ds.is_little_endian else '>'
        byte_depth = nominal_depth // 8
        fmt = 'B' if byte_depth == 1 else 'H'
        actual_depth = nominal_depth

        for seg in [ii for ii in [r_lut, g_lut, b_lut, a_lut] if ii]:
            len_seg = len(seg) // byte_depth
            s_fmt = endianness + str(len_seg) + fmt
            lut = _expand_segmented_lut(unpack(s_fmt, seg), s_fmt)
            luts.append(np.asarray(lut, dtype=dtype))
    else:
        raise ValueError("No suitable Palette Color Lookup Table Module found")

    if actual_depth not in [8, 16]:
        raise ValueError(
            "The bit depth of the LUT data '{:.1f}' is invalid (only 8 or 16 "
            "bits per entry allowed)".format(actual_depth)
        )

    lut_lengths = [len(ii) for ii in luts]
    if not all(ii == lut_lengths[0] for ii in lut_lengths[1:]):
        raise ValueError("LUT data must be the same length")

    # IVs < `first_map` get set to first LUT entry (i.e. index 0)
    clipped_iv = np.zeros(arr.shape, dtype=dtype)
    # IVs >= `first_map` are mapped by the Palette Color LUTs
    # `first_map` may be negative, positive or 0
    mapped_pixels = arr >= first_map
    clipped_iv[mapped_pixels] = arr[mapped_pixels] - first_map
    # IVs > number of entries get set to last entry
    np.clip(clipped_iv, 0, nr_entries - 1, out=clipped_iv)

    # Output array may be RGB or RGBA
    out = np.empty(list(arr.shape) + [len(luts)], dtype=dtype)
    for ii, lut in enumerate(luts):
        out[..., ii] = lut[clipped_iv]

    return out