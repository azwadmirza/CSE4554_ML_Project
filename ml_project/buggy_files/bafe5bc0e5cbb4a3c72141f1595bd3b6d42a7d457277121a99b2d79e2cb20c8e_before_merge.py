def _get_gadget_format(filename):
    # check and return gadget binary format with file endianness
    ff = open(filename, 'rb')
    (rhead,) = struct.unpack('<I', ff.read(4))
    ff.close()
    if (rhead == 134217728):
        return 2, '>'
    elif (rhead == 8):
        return 2, '<'
    elif (rhead == 65536):
        return 1, '>'
    elif (rhead == 256):
        return 1, '<'
    else:
        raise RuntimeError("Incorrect Gadget format %s!" % str(rhead))