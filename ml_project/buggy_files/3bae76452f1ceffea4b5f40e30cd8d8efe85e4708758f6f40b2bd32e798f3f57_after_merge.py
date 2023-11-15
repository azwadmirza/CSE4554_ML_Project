def write(fname, data, header, **kwargs):
    """
    Take a data header pair and write a FITS file.

    Parameters
    ----------
    fname : `str`
        File name, with extension

    data : `numpy.ndarray`
        n-dimensional data array

    header : `dict`
        A header dictionary
    """
    # Copy header so the one in memory is left alone while changing it for
    # write.
    header = header.copy()

    # The comments need to be added to the header separately from the normal
    # kwargs. Find and deal with them:
    fits_header = fits.Header()
    # Check Header
    key_comments = header.pop('KEYCOMMENTS', False)

    for k, v in header.items():
        if isinstance(v, fits.header._HeaderCommentaryCards):
            if k == 'comments':
                comments = str(v).split('\n')
                for com in comments:
                    fits_header.add_comments(com)
            elif k == 'history':
                hists = str(v).split('\n')
                for hist in hists:
                    fits_header.add_history(hist)
            elif k != '':
                fits_header.append(fits.Card(k, str(v).split('\n')))

        else:
            fits_header.append(fits.Card(k, v))

    if isinstance(key_comments, dict):
        for k, v in key_comments.items():
            # Check that the Card for the comment exists before trying to write to it.
            if k in fits_header:
                fits_header.comments[k] = v
    elif key_comments:
        raise TypeError("KEYCOMMENTS must be a dictionary")

    if isinstance(fname, str):
        fname = os.path.expanduser(fname)

    fitskwargs = {'output_verify': 'fix'}
    fitskwargs.update(kwargs)
    fits.writeto(fname, data, header=fits_header, **fitskwargs)