def _data_bytes_to_shaped_array(data_bytes, lbpack, boundary_packing,
                                data_shape, data_type, mdi,
                                mask=None):
    """
    Convert the already read binary data payload into a numpy array, unpacking
    and decompressing as per the F3 specification.

    """
    if lbpack.n1 in (0, 2):
        data = np.frombuffer(data_bytes, dtype=data_type)
    elif lbpack.n1 == 1:
        if mo_pack is not None:
            try:
                decompress_wgdos = mo_pack.decompress_wgdos
            except AttributeError:
                decompress_wgdos = mo_pack.unpack_wgdos
        else:
            msg = 'Unpacking PP fields with LBPACK of {} ' \
                  'requires mo_pack to be installed'.format(lbpack.n1)
            raise ValueError(msg)
        data = decompress_wgdos(data_bytes, data_shape[0], data_shape[1], mdi)
    elif lbpack.n1 == 4:
        if mo_pack is not None and hasattr(mo_pack, 'decompress_rle'):
            decompress_rle = mo_pack.decompress_rle
        else:
            msg = 'Unpacking PP fields with LBPACK of {} ' \
                  'requires mo_pack to be installed'.format(lbpack.n1)
            raise ValueError(msg)
        data = decompress_rle(data_bytes, data_shape[0], data_shape[1], mdi)
    else:
        raise iris.exceptions.NotYetImplementedError(
            'PP fields with LBPACK of %s are not yet supported.' % lbpack)

    # Ensure we have a writeable data buffer.
    # NOTE: "data.setflags(write=True)" is not valid for numpy >= 1.16.0.
    if not data.flags['WRITEABLE']:
        data = data.copy()

    # Ensure the data is in the native byte order
    if not data.dtype.isnative:
        data.byteswap(True)
        data.dtype = data.dtype.newbyteorder('=')

    if boundary_packing is not None:
        # Convert a long string of numbers into a "lateral boundary
        # condition" array, which is split into 4 quartiles, North
        # East, South, West and where North and South contain the corners.
        compressed_data = data
        data = np.ma.masked_all(data_shape)
        data.fill_value = mdi

        boundary_height = boundary_packing.y_halo + boundary_packing.rim_width
        boundary_width = boundary_packing.x_halo + boundary_packing.rim_width
        y_height, x_width = data_shape
        # The height of the east and west components.
        mid_height = y_height - 2 * boundary_height

        n_s_shape = boundary_height, x_width
        e_w_shape = mid_height, boundary_width

        # Keep track of our current position in the array.
        current_posn = 0

        north = compressed_data[:boundary_height*x_width]
        current_posn += len(north)
        data[-boundary_height:, :] = north.reshape(*n_s_shape)

        east = compressed_data[current_posn:
                               current_posn + boundary_width * mid_height]
        current_posn += len(east)
        data[boundary_height:-boundary_height,
             -boundary_width:] = east.reshape(*e_w_shape)

        south = compressed_data[current_posn:
                                current_posn + boundary_height * x_width]
        current_posn += len(south)
        data[:boundary_height, :] = south.reshape(*n_s_shape)

        west = compressed_data[current_posn:
                               current_posn + boundary_width * mid_height]
        current_posn += len(west)
        data[boundary_height:-boundary_height,
             :boundary_width] = west.reshape(*e_w_shape)

    elif lbpack.n2 == 2:
        if mask is None:
            # If we are given no mask to apply, then just return raw data, even
            # though it does not have the correct shape.
            # For dask-delayed loading, this means that mask, data and the
            # combination can be properly handled within a dask graph.
            # However, we still mask any MDI values in the array (below).
            pass
        else:
            land_mask = mask.data.astype(np.bool)
            sea_mask = ~land_mask
            new_data = np.ma.masked_all(land_mask.shape)
            new_data.fill_value = mdi
            if lbpack.n3 == 1:
                # Land mask packed data.
                # Sometimes the data comes in longer than it should be (i.e. it
                # looks like the compressed data is compressed, but the
                # trailing data hasn't been clipped off!).
                new_data[land_mask] = data[:land_mask.sum()]
            elif lbpack.n3 == 2:
                # Sea mask packed data.
                new_data[sea_mask] = data[:sea_mask.sum()]
            else:
                raise ValueError('Unsupported mask compression.')
            data = new_data

    else:
        # Reform in row-column order
        data.shape = data_shape

    # Mask the array
    if mdi in data:
        data = ma.masked_values(data, mdi, copy=False)

    return data