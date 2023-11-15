def custom(img, vertices):
    """Create an custom polygon ROI.

        Inputs:
        img           = An RGB or grayscale image to plot the ROI on in debug mode.
        vertices      = List of vertices of the desired polygon ROI

        Outputs:
        roi_contour   = An ROI set of points (contour).
        roi_hierarchy = The hierarchy of ROI contour(s).

        :param img: numpy.ndarray
        :param vertices: list
        :return roi_contour: list
        :return roi_hierarchy: numpy.ndarray
        """
    # Autoincrement the device counter
    params.device += 1

    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    roi_contour = [np.array(vertices, dtype=np.int32)]
    roi_hierarchy = np.array([[[-1, -1, -1, -1]]], dtype=np.int32)

    if params.debug is not None:
        _draw_roi(img=img, roi_contour=roi_contour)

    # Check that the ROI doesn't go off the screen
    for i in vertices:
        (x, y) = i
        if x < 0 or x > width or y < 0 or y > height:
            fatal_error("An ROI extends outside of the image!")

    return roi_contour, roi_hierarchy