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

    # Store user debug
    debug = params.debug

    # Temporarily disable debug
    params.debug = None

    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]
    overlap_img = np.zeros((height, width))

    # Initialize a binary image of the circle that will contain all ROI
    all_roi_img = np.zeros((height, width), dtype=np.uint8)
    roi_contour = []
    roi_hierarchy = []
    # Grid of ROIs
    if (type(coord) == tuple) and ((nrows and ncols) is not None) and (type(spacing) == tuple):
        # Loop over each row
        for i in range(0, nrows):
            # The upper left corner is the y starting coordinate + the ROI offset * the vertical spacing
            y = coord[1] + i * spacing[1]
            # Loop over each column
            for j in range(0, ncols):
                # Initialize a binary image for each circle
                bin_img = np.zeros((height, width), dtype=np.uint8)
                # The upper left corner is the x starting coordinate + the ROI offset * the
                # horizontal spacing between chips
                x = coord[0] + j * spacing[0]
                # Check whether the ROI is correctly bounded inside the image
                if x - radius < 0 or x + radius > width or y - radius < 0 or y + radius > height:
                    fatal_error("An ROI extends outside of the image!")
                # Draw the circle on the binary images
                # Keep track of all roi
                all_roi_img = cv2.circle(all_roi_img, (x, y), radius, 255, -1)
                # Keep track of each roi individually to check overlapping
                circle_img = cv2.circle(bin_img, (x, y), radius, 255, -1)
                overlap_img = overlap_img + circle_img
                # Make a list of contours and hierarchies
                _, rc, rh = cv2.findContours(circle_img, cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_NONE)
                roi_contour.append(rc)
                roi_hierarchy.append(rh)

    # User specified ROI centers
    elif (type(coord) == list) and ((nrows and ncols) is None) and (spacing is None):
        for i in range(0, len(coord)):
            # Initialize a binary image for each circle
            bin_img = np.zeros((height, width), dtype=np.uint8)
            y = coord[i][1]
            x = coord[i][0]
            if x - radius < 0 or x + radius > width or y - radius < 0 or y + radius > height:
                fatal_error("An ROI extends outside of the image!")
            # Draw the circle on the binary image
            # Keep track of all roi
            all_roi_img = cv2.circle(all_roi_img, (x, y), radius, 255, -1)
            # Keep track of each roi individually to check overlapping
            circle_img = cv2.circle(bin_img, (x, y), radius, 255, -1)
            overlap_img = overlap_img + circle_img
            # Make a list of contours and hierarchies
            _, rc, rh = cv2.findContours(circle_img, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_NONE)
            roi_contour.append(rc)
            roi_hierarchy.append(rh)
    else:
        fatal_error("Function can either make a grid of ROIs (user must provide nrows, ncols, spacing, and coord) "
                    "or take custom ROI coordinates (user must provide only a list of tuples to 'coord' parameter). "
                    "Both options require a user-defined radius as well")

    if np.amax(overlap_img) > 255:
        print("WARNING: Two or more of the user defined regions of interest overlap! "
              "If you only see one ROI then they may overlap exactly.")

    # Reset debug
    params.debug = debug

    # Draw the ROIs if requested
    if params.debug is not None:
        # Create an array of contours and list of hierarchy for debug image
        roi_contour1, roi_hierarchy1 = cv2.findContours(all_roi_img, cv2.RETR_TREE,
                                                        cv2.CHAIN_APPROX_NONE)[-2:]
        _draw_roi(img=img, roi_contour=roi_contour1)

    return roi_contour, roi_hierarchy