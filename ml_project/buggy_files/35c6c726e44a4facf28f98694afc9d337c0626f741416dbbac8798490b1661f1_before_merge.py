def multi(img, coord, radius, spacing=None, nrows=None, ncols=None):
    """Create multiple circular ROIs on a single image
    Inputs
    img            = Input image data.
    coord          = Two-element tuple of the center of the top left object (x,y) or a list of tuples identifying the center of each roi [(x1,y1),(x2,y2)]
    radius         = A single radius for all ROIs.
    spacing        = Two-element tuple of the horizontal and vertical spacing between ROIs, (x,y). Ignored if `coord` is a list and `rows` and `cols` are None.
    nrows          = Number of rows in ROI layout. Should be missing or None if each center coordinate pair is listed.
    ncols          = Number of columns in ROI layout. Should be missing or None if each center coordinate pair is listed.

    Returns:
    roi_contour           = list of roi contours
    roi_hierarchy         = list of roi hierarchies

    :param img: numpy.ndarray
    :param coord: tuple, list
    :param radius: int
    :param spacing: tuple
    :param nrows: int
    :param ncols: int
    :return mask: numpy.ndarray
    """

    # Autoincrement the device counter
    params.device += 1

    # Initialize ROI list
    rois = []

    # Store user debug
    debug = params.debug

    # Temporarily disable debug
    params.debug = None

    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    # Initialize a binary image of the circle
    bin_img = np.zeros((height, width), dtype=np.uint8)
    roi_contour = []
    roi_hierarchy = []
    # Grid of ROIs
    if (type(coord) == tuple) and ((nrows and ncols) is not None):
        # Loop over each row
        for i in range(0, nrows):
            # The upper left corner is the y starting coordinate + the ROI offset * the vertical spacing
            y = coord[1] + i * spacing[1]
            # Loop over each column
            for j in range(0, ncols):
                # The upper left corner is the x starting coordinate + the ROI offset * the
                # horizontal spacing between chips
                x = coord[0] + j * spacing[0]
                # Create a chip ROI
                rois.append(circle(img=img, x=x, y=y, r=radius))
                # Draw the circle on the binary image
                cv2.circle(bin_img, (x, y), radius, 255, -1)
                # Make a list of contours and hierarchies
                roi_contour.append(cv2.findContours(np.copy(bin_img), cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)[-2:][0])
                roi_hierarchy.append(cv2.findContours(np.copy(bin_img), cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_NONE)[-2:][1])
                # Create an array of contours and list of hierarchy for when debug is set to 'plot'
                roi_contour1, roi_hierarchy1 = cv2.findContours(np.copy(bin_img), cv2.RETR_TREE,
                                                                cv2.CHAIN_APPROX_NONE)[-2:]

    # User specified ROI centers
    elif (type(coord) == list) and ((nrows and ncols) is None):
        for i in range(0, len(coord)):
            y = coord[i][1]
            x = coord[i][0]
            rois.append(circle(img=img, x=x, y=y, r=radius))
            # Draw the circle on the binary image
            cv2.circle(bin_img, (x, y), radius, 255, -1)
            #  Make a list of contours and hierarchies
            roi_contour.append(cv2.findContours(np.copy(bin_img), cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_NONE)[-2:][0])
            roi_hierarchy.append(cv2.findContours(np.copy(bin_img), cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_NONE)[-2:][1])
            # Create an array of contours and list of hierarchy for when debug is set to 'plot'
            roi_contour1, roi_hierarchy1 = cv2.findContours(np.copy(bin_img), cv2.RETR_TREE,
                                                            cv2.CHAIN_APPROX_NONE)[-2:]

    else:
        fatal_error("Function can either make a grid of ROIs (user must provide nrows, ncols, spacing, and coord) "
                    "or take custom ROI coordinates (user must provide a list of tuples to 'coord' parameter)")
    # Reset debug
    params.debug = debug

    # Draw the ROIs if requested
    if params.debug is not None:
        _draw_roi(img=img, roi_contour=roi_contour1)

    return roi_contour, roi_hierarchy