def spd_reader(filename,
               endianess='<',
               nav_units=None,
               spc_fname=None,
               ipr_fname=None,
               load_all_spc=False,
               **kwargs):
    """
    Read data from an SPD spectral map specified by filename.

    Parameters
    ----------
    filename : str
        Name of SPD file to read
    endianess : char
        Byte-order of data to read
    nav_units : 'nm', 'um', or None
        Default navigation units for EDAX data is in microns, so this is the
        default unit to save in the signal. Can also be specified as 'nm',
        which will output a signal with nm scale instead.
    spc_fname : None or str
        Name of file from which to read the spectral calibration. If data
        was exported fully from EDAX TEAM software, an .spc file with the
        same name as the .spd should be present.
        If `None`, the default filename will be searched for.
        Otherwise, the name of the .spc file to use for calibration can
        be explicitly given as a string.
    ipr_fname : None or str
        Name of file from which to read the spatial calibration. If data
        was exported fully from EDAX TEAM software, an .ipr file with the
        same name as the .spd (plus a \"_Img\" suffix) should be present.
        If `None`, the default filename will be searched for.
        Otherwise, the name of the .ipr file to use for spatial calibration
        can be explicitly given as a string.
    load_all_spc : bool
        Switch to control if all of the .spc header is read, or just the
        important parts for import into HyperSpy
    kwargs**
        Remaining arguments are passed to the Numpy ``memmap`` function

    Returns
    -------
    list
        list with dictionary of signal information to be passed back to
        hyperspy.io.load_with_reader
    """
    with open(filename, 'rb') as f:
        spd_header = np.fromfile(f,
                                 dtype=get_spd_dtype_list(endianess),
                                 count=1)

        original_metadata = {'spd_header': sarray2dict(spd_header)}

        # dimensions of map data:
        nx = original_metadata['spd_header']['nPoints']
        ny = original_metadata['spd_header']['nLines']
        nz = original_metadata['spd_header']['nChannels']
        data_offset = original_metadata['spd_header']['dataOffset']
        data_type = {'1': 'u1',
                     '2': 'u2',
                     '4': 'u4'}[str(original_metadata['spd_header'][
                         'countBytes'])]
        lazy = kwargs.pop('lazy', False)
        mode = kwargs.pop('mode', 'c')
        if lazy:
            mode = 'r'

        # Read data from file into a numpy memmap object
        data = np.memmap(f, mode=mode, offset=data_offset, dtype=data_type,
                         **kwargs).squeeze().reshape((nz, nx, ny), order='F').T

    # Convert char arrays to strings:
    original_metadata['spd_header']['tag'] = \
        spd_header['tag'][0].view('S16')[0]
    # fName is the name of the .bmp (and .ipr) file of the map
    original_metadata['spd_header']['fName'] = \
        spd_header['fName'][0].view('S120')[0]

    # Get name of .spc file from the .spd map (if not explicitly given):
    if spc_fname is None:
        spc_path = os.path.dirname(filename)
        spc_basename = os.path.splitext(os.path.basename(filename))[
            0] + '.spc'
        spc_fname = os.path.join(spc_path, spc_basename)

    # Get name of .ipr file from bitmap image (if not explicitly given):
    if ipr_fname is None:
        ipr_basename = os.path.splitext(
            os.path.basename(
                original_metadata['spd_header'][
                    'fName']))[0].decode() + '.ipr'
        ipr_path = os.path.dirname(filename)
        ipr_fname = os.path.join(ipr_path, ipr_basename)

    # Flags to control reading of files
    read_spc = os.path.isfile(spc_fname)
    read_ipr = os.path.isfile(ipr_fname)

    # Read the .ipr header (if possible)
    if read_ipr:
        with open(ipr_fname, 'rb') as f:
            _logger.debug(' From .spd reader - '
                          'reading .ipr {}'.format(ipr_fname))
            ipr_header = __get_ipr_header(f, endianess)
            original_metadata['ipr_header'] = sarray2dict(ipr_header)
    else:
        _logger.warning('Could not find .ipr file named {}.\n'
                        'No spatial calibration will be loaded.'
                        '\n'.format(ipr_fname))

    # Read the .spc header (if possible)
    if read_spc:
        with open(spc_fname, 'rb') as f:
            _logger.debug(' From .spd reader - '
                          'reading .spc {}'.format(spc_fname))
            spc_header = __get_spc_header(f, endianess, load_all_spc)
            spc_dict = sarray2dict(spc_header)
            original_metadata['spc_header'] = spc_dict
    else:
        _logger.warning('Could not find .spc file named {}.\n'
                        'No spectral metadata will be loaded.'
                        '\n'.format(spc_fname))

    # create the energy axis dictionary:
    energy_axis = {
        'size': data.shape[2],
        'index_in_array': 2,
        'name': 'Energy',
        'scale': original_metadata['spc_header']['evPerChan'] / 1000.0 if
        read_spc else 1,
        'offset': original_metadata['spc_header']['startEnergy'] if
        read_spc else 1,
        'units': 'keV' if read_spc else t.Undefined,
    }

    # Handle navigation units input:
    scale = 1000 if nav_units == 'nm' else 1
    if nav_units is not 'nm':
        if nav_units not in [None, 'um']:
            _logger.warning("Did not understand nav_units input \"{}\". "
                            "Defaulting to microns.\n".format(nav_units))
        nav_units = r'$\mu m$'

    # Create navigation axes dictionaries:
    x_axis = {
        'size': data.shape[1],
        'index_in_array': 1,
        'name': 'x',
        'scale': original_metadata['ipr_header']['mppX'] * scale if read_ipr
        else 1,
        'offset': 0,
        'units': nav_units if read_ipr else t.Undefined,
    }

    y_axis = {
        'size': data.shape[0],
        'index_in_array': 0,
        'name': 'y',
        'scale': original_metadata['ipr_header']['mppY'] * scale if read_ipr
        else 1,
        'offset': 0,
        'units': nav_units if read_ipr else t.Undefined,
    }

    # Assign metadata for spectrum image:
    metadata = {'General': {'original_filename': os.path.split(filename)[1],
                            'title': 'EDS Spectrum Image'},
                "Signal": {'signal_type': "EDS_SEM",
                           'record_by': 'spectrum', }, }

    # Add spectral calibration and elements (if present):
    if read_spc:
        metadata = _add_spc_metadata(metadata, spc_dict)

    # Define navigation and signal axes:
    axes = [y_axis, x_axis, energy_axis]

    dictionary = {'data': data,
                  'axes': axes,
                  'metadata': metadata,
                  'original_metadata': original_metadata}

    return [dictionary, ]