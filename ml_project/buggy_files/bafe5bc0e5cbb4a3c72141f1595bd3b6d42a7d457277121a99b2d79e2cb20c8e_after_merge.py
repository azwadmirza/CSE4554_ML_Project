def _get_gadget_format(filename, header_size):
    # check and return gadget binary format with file endianness
    ff = open(filename, 'rb')
    (rhead,) = struct.unpack('<I', ff.read(4))
    ff.close()
    if (rhead == _byte_swap_32(8)):
        return 2, '>'
    elif (rhead == 8):
        return 2, '<'
    elif (rhead == _byte_swap_32(header_size)):
        return 1, '>'
    elif (rhead == header_size):
        return 1, '<'
    else:
        raise RuntimeError("Incorrect Gadget format %s!" % str(rhead))