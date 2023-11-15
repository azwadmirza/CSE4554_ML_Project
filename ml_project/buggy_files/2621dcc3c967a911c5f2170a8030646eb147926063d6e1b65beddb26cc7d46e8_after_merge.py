def add_overlay(orig, area, coast_dir, color=(0, 0, 0), width=0.5, resolution=None,
                level_coast=1, level_borders=1, fill_value=None):
    """Add coastline and political borders to image.

    Uses ``color`` for feature colors where ``color`` is a 3-element tuple
    of integers between 0 and 255 representing (R, G, B).

    .. warning::

        This function currently loses the data mask (alpha band).

    ``resolution`` is chosen automatically if None (default), otherwise it should be one of:

    +-----+-------------------------+---------+
    | 'f' | Full resolution         | 0.04 km |
    | 'h' | High resolution         | 0.2 km  |
    | 'i' | Intermediate resolution | 1.0 km  |
    | 'l' | Low resolution          | 5.0 km  |
    | 'c' | Crude resolution        | 25  km  |
    +-----+-------------------------+---------+

    """

    if area is None:
        raise ValueError("Area of image is None, can't add overlay.")

    from pycoast import ContourWriterAGG
    if isinstance(area, str):
        area = get_area_def(area)
    LOG.info("Add coastlines and political borders to image.")

    if resolution is None:

        x_resolution = ((area.area_extent[2] -
                         area.area_extent[0]) /
                        area.x_size)
        y_resolution = ((area.area_extent[3] -
                         area.area_extent[1]) /
                        area.y_size)
        res = min(x_resolution, y_resolution)

        if res > 25000:
            resolution = "c"
        elif res > 5000:
            resolution = "l"
        elif res > 1000:
            resolution = "i"
        elif res > 200:
            resolution = "h"
        else:
            resolution = "f"

        LOG.debug("Automagically choose resolution %s", resolution)

    if hasattr(orig, 'convert'):
        # image must be in RGB space to work with pycoast/pydecorate
        orig = orig.convert('RGBA' if orig.mode.endswith('A') else 'RGB')
    elif not orig.mode.startswith('RGB'):
        raise RuntimeError("'trollimage' 1.6+ required to support adding "
                           "overlays/decorations to non-RGB data.")
    img = orig.pil_image(fill_value=fill_value)
    cw_ = ContourWriterAGG(coast_dir)
    cw_.add_coastlines(img, area, outline=color,
                       resolution=resolution, width=width, level=level_coast)
    cw_.add_borders(img, area, outline=color,
                    resolution=resolution, width=width, level=level_borders)

    arr = da.from_array(np.array(img) / 255.0, chunks=CHUNK_SIZE)

    new_data = xr.DataArray(arr, dims=['y', 'x', 'bands'],
                            coords={'y': orig.data.coords['y'],
                                    'x': orig.data.coords['x'],
                                    'bands': list(img.mode)},
                            attrs=orig.data.attrs)
    return XRImage(new_data)