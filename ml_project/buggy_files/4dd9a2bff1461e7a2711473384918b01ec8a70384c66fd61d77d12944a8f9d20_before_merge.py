def add_overlay(orig, area, coast_dir, color=(0, 0, 0), width=0.5, resolution=None, level_coast=1, level_borders=1):
    """Add coastline and political borders to image, using *color* (tuple
    of integers between 0 and 255).
    Warning: Loses the masks !
    *resolution* is chosen automatically if None (default), otherwise it should be one of:
    +-----+-------------------------+---------+
    | 'f' | Full resolution         | 0.04 km |
    | 'h' | High resolution         | 0.2 km  |
    | 'i' | Intermediate resolution | 1.0 km  |
    | 'l' | Low resolution          | 5.0 km  |
    | 'c' | Crude resolution        | 25  km  |
    +-----+-------------------------+---------+
    """
    img = orig.pil_image()

    if area is None:
        raise ValueError("Area of image is None, can't add overlay.")

    from pycoast import ContourWriterAGG
    from satpy.resample import get_area_def
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

        LOG.debug("Automagically choose resolution " + resolution)

    if img.mode.endswith('A'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')

    cw_ = ContourWriterAGG(coast_dir)
    cw_.add_coastlines(img, area, outline=color,
                       resolution=resolution, width=width, level=level_coast)
    cw_.add_borders(img, area, outline=color,
                    resolution=resolution, width=width, level=level_borders)

    arr = np.array(img)

    if orig.mode == 'L':
        orig.channels[0] = np.ma.array(arr[:, :, 0] / 255.0)
    elif orig.mode == 'LA':
        orig.channels[0] = np.ma.array(arr[:, :, 0] / 255.0)
        orig.channels[1] = np.ma.array(arr[:, :, -1] / 255.0)
    else:
        for idx in range(len(orig.channels)):
            orig.channels[idx] = np.ma.array(arr[:, :, idx] / 255.0)