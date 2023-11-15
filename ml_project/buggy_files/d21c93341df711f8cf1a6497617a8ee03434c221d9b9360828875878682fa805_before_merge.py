def make_colormap(ctuple_list, name=None, interpolate=True):
    """
    This generates a custom colormap based on the colors and spacings you
    provide.  Enter a ctuple_list, which consists of tuples of (color, spacing)
    to return a colormap appropriate for use in yt.  If you specify a 
    name, it will automatically be added to the current session as a valid
    colormap.
    
    Output colormap is in the format yt expects for adding a colormap to the 
    current session: a dictionary with the appropriate RGB channels each 
    consisting of a 256x3 array :
    First number is the number at which we are defining a color breakpoint
    Second number is the (0..1) number to interpolate to when coming *from below*
    Third number is the (0..1) number to interpolate to when coming *from above*

    Parameters
    ----------

    ctuple_list: list of (color, float) tuples
        The ctuple_list consists of pairs of (color, interval) tuples
        identifying the colors to use in the colormap and the intervals
        they take to change to the next color in the list.  A color can
        either be a string of the name of a color, or it can be an array
        of 3 floats, each representing the intensity of R, G, and B on
        a scale of 0 to 1.  Valid color names and their equivalent
        arrays are listed below.

        Any interval can be given for the different color tuples, and
        the total of all the intervals will be scaled to the 256 output
        elements.

        If a ctuple_list ends with a color and a non-zero interval, 
        a white 0-interval would be added to the end to finish the 
        interpolation.  To avoid finishing with white, specify your own 
        zero-interval color at the end.

    name: string, optional
        If you wish this colormap to be added as a valid colormap to the 
        current session, specify a name here.  Default: None

    interpolation: boolean, optional
        Designates whether or not the colormap will interpolate between
        the colors provided or just give solid colors across the intervals.
        Default: True

    Preset Color Options
    --------------------

    'white' : np.array([255, 255, 255 ])/255.
    'gray' : np.array([130, 130, 130])/255.
    'dgray' : np.array([80, 80, 80])/255.
    'black' : np.array([0, 0, 0])/255.
    'blue' : np.array([0, 0, 255])/255.
    'dblue' : np.array([0, 0, 160])/255.
    'purple' : np.array([100, 0, 200])/255.
    'dpurple' : np.array([66, 0, 133])/255.
    'dred' : np.array([160, 0, 0])/255.
    'red' : np.array([255, 0, 0])/255.
    'orange' : np.array([255, 128, 0])/255.
    'dorange' : np.array([200,100, 0])/255.
    'yellow' : np.array([255, 255, 0])/255.
    'dyellow' : np.array([200, 200, 0])/255.
    'green' : np.array([0, 255, 0])/255.
    'dgreen' : np.array([0, 160, 0])/255.

    Examples
    --------

    To obtain a colormap that starts at black with equal intervals in green, 
    blue, red, yellow in that order and interpolation between those colors.  
    (In reality, it starts at black, takes an interval of 10 to interpolate to 
    green, then an interval of 10 to interpolate to blue, then an interval of 
    10 to interpolate to red.)

    >>> cm = make_colormap([('black', 10), ('green', 10), ('blue', 10),
    ...                     ('red', 0)])

    To add a colormap that has five equal blocks of solid major colors to
    the current session as "steps":

    >>> make_colormap([('red', 10), ('orange', 10), ('yellow', 10),
    ...                ('green', 10), ('blue', 10)], name="steps",
    ...               interpolate=False)

    To add a colormap that looks like the French flag (i.e. equal bands of 
    blue, white, and red) using your own RGB keys, then to display it:

    >>> make_colormap([([0,0,1], 10), ([1,1,1], 10), ([1,0,0], 10)], 
    ...               name='french_flag', interpolate=False)
    >>> show_colormaps(['french_flag'])

    """
    # aliases for different colors
    color_dict = {
    'white' : np.array([255, 255, 255 ])/255.,
    'gray' : np.array([130, 130, 130])/255.,
    'dgray' : np.array([80, 80, 80])/255.,
    'black' : np.array([0, 0, 0])/255.,
    'blue' : np.array([0, 0, 255])/255.,
    'dblue' : np.array([0, 0, 160])/255.,
    'purple' : np.array([100, 0, 200])/255.,
    'dpurple' : np.array([66, 0, 133])/255.,
    'dred' : np.array([160, 0, 0])/255.,
    'red' : np.array([255, 0, 0])/255.,
    'orange' : np.array([255, 128, 0])/255.,
    'dorange' : np.array([200,100, 0])/255.,
    'yellow' : np.array([255, 255, 0])/255.,
    'dyellow' : np.array([200, 200, 0])/255.,
    'green' : np.array([0, 255, 0])/255.,
    'dgreen' : np.array([0, 160, 0])/255.}

    cmap = np.zeros((256,3))

    # If the user provides a list with a non-zero final interval, it
    # doesn't make sense because you have an interval but no final
    # color to which it interpolates.  So provide a 0-length white final
    # interval to end the previous interval in white.
    if ctuple_list[-1][1] != 0:
        ctuple_list.append(('white', 0))

    # Figure out how many intervals there are total.
    rolling_index = 0
    for i, (color, interval) in enumerate(ctuple_list):
        if isinstance(color, string_types):
            ctuple_list[i] = (color_dict[color], interval)
        rolling_index += interval
    scale = 256./rolling_index
    n = len(ctuple_list)

    # Step through each ctuple and interpolate from one color to the
    # next over the interval provided
    rolling_index = 0
    for i in range(n-1):
        color, interval = ctuple_list[i]
        interval *= scale
        next_index = rolling_index + interval
        next_color, next_interval = ctuple_list[i+1]

        if not interpolate:
            next_color = color

        # Interpolate the R, G, and B channels from one color to the next
        # Use np.round to make sure you're on a discrete index
        interval = np.round(next_index)-np.round(rolling_index)
        for j in np.arange(3):
            cmap[int(np.rint(rolling_index)):int(np.rint(next_index)), j] = \
                np.linspace(color[j], next_color[j], interval)

        rolling_index = next_index

    # Return a dictionary with the appropriate RGB channels each consisting of
    # a 256x3 array in the format that is expected by add_cmap() to add a 
    # colormap to the session.

    # The format is as follows:
    #   First number is the number at which we are defining a color breakpoint
    #   Second number is the (0..1) number to interpolate to when coming *from below*
    #   Third number is the (0..1) number to interpolate to when coming *from above*
    _vs = np.linspace(0,1,256)
    cdict = {'red':   np.transpose([_vs, cmap[:,0], cmap[:,0]]),
             'green': np.transpose([_vs, cmap[:,1], cmap[:,1]]),
             'blue':  np.transpose([_vs, cmap[:,2], cmap[:,2]])}

    if name is not None:
        add_cmap(name, cdict)

    return cdict