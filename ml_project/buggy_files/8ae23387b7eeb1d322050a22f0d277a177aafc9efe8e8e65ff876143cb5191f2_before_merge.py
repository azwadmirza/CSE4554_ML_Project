def backprojection(calibrated_event_list, pixel_size=(1., 1.) * u.arcsec,
                   image_dim=(64, 64) * u.pix):
    """
    Given a stacked calibrated event list fits file create a back
    projection image.

    .. warning:: The image is not in the right orientation!

    Parameters
    ----------
    calibrated_event_list : string
        filename of a RHESSI calibrated event list
    pixel_size : `~astropy.units.Quantity` instance
        the size of the pixels in arcseconds. Default is (1,1).
    image_dim : `~astropy.units.Quantity` instance
        the size of the output image in number of pixels

    Returns
    -------
    out : RHESSImap
        Return a backprojection map.

    Examples
    --------
    >>> import sunpy.data.sample
    >>> import sunpy.instr.rhessi as rhessi
    >>> map = rhessi.backprojection(sunpy.data.sample.RHESSI_EVENT_LIST)   # doctest: +SKIP
    >>> map.peek()   # doctest: +SKIP

    """
    if not isinstance(pixel_size, u.Quantity):
        raise ValueError("Must be astropy Quantity in arcseconds")
    try:
        pixel_size = pixel_size.to(u.arcsec)
    except:
        raise ValueError("'{0}' is not a valid pixel_size unit".format(pixel_size.unit))
    if not (isinstance(image_dim, u.Quantity) and image_dim.unit == 'pix'):
        raise ValueError("Must be astropy Quantity in pixels")

    afits = fits.open(calibrated_event_list)
    info_parameters = afits[2]
    xyoffset = info_parameters.data.field('USED_XYOFFSET')[0]
    time_range = TimeRange(info_parameters.data.field('ABSOLUTE_TIME_RANGE')[0])

    image = np.zeros(image_dim.value)

    # find out what detectors were used
    det_index_mask = afits[1].data.field('det_index_mask')[0]
    detector_list = (np.arange(9)+1) * np.array(det_index_mask)
    for detector in detector_list:
        if detector > 0:
            image = image + _backproject(calibrated_event_list, detector=detector, pixel_size=pixel_size.value,
                                         image_dim=image_dim.value)

    dict_header = {
        "DATE-OBS": time_range.center().strftime("%Y-%m-%d %H:%M:%S"),
        "CDELT1": pixel_size[0],
        "NAXIS1": image_dim[0],
        "CRVAL1": xyoffset[0],
        "CRPIX1": image_dim[0].value/2 + 0.5,
        "CUNIT1": "arcsec",
        "CTYPE1": "HPLN-TAN",
        "CDELT2": pixel_size[1],
        "NAXIS2": image_dim[1],
        "CRVAL2": xyoffset[1],
        "CRPIX2": image_dim[0].value/2 + 0.5,
        "CUNIT2": "arcsec",
        "CTYPE2": "HPLT-TAN",
        "HGLT_OBS": 0,
        "HGLN_OBS": 0,
        "RSUN_OBS": solar_semidiameter_angular_size(time_range.center()).value,
        "RSUN_REF": sunpy.sun.constants.radius.value,
        "DSUN_OBS": sunearth_distance(time_range.center()) * sunpy.sun.constants.au.value
    }

    header = sunpy.map.MetaDict(dict_header)
    result_map = sunpy.map.Map(image, header)

    return result_map