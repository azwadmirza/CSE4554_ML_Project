    def _validate_header(filename):
        '''
        This method automatically detects whether the Gadget file is big/little endian
        and is not corrupt/invalid using the first 4 bytes in the file.  It returns a
        tuple of (Valid, endianswap) where Valid is a boolean that is true if the file
        is a Gadget binary file, and endianswap is the endianness character '>' or '<'.
        '''
        try:
            f = open(filename, 'rb')
        except IOError:
            try:
                f = open(filename + ".0")
            except IOError:
                return False, 1

        # First int32 is 256 for a Gadget2 binary file with SnapFormat=1,
        # 8 for a Gadget2 binary file with SnapFormat=2 file,
        # or the byte swapped equivalents (65536 and 134217728).
        # The int32 following the header (first 4+256 bytes) must equal this
        # number.
        try:
            (rhead,) = struct.unpack('<I', f.read(4))
        except struct.error:
            f.close()
            return False, 1
        # Use value to check endianness
        if rhead == 256:
            endianswap = '<'
        elif rhead == 65536:
            endianswap = '>'
        elif rhead in (8, 134217728):
            # This is only true for snapshot format 2
            # we do not currently support double precision
            # snap format 2 data
            f.close()
            return True, 'f4'
        else:
            f.close()
            return False, 1
        # Read in particle number from header
        np0 = sum(struct.unpack(endianswap + 'IIIIII', f.read(6 * 4)))
        # Read in size of position block. It should be 4 bytes per float,
        # with 3 coordinates (x,y,z) per particle. (12 bytes per particle)
        f.seek(4 + 256 + 4, 0)
        np1 = struct.unpack(endianswap + 'I', f.read(4))[0] / (4 * 3)
        f.close()
        # Compare
        if np0 == np1:
            return True, 'f4'
        elif np1 == 2*np0:
            return True, 'f8'
        else:
            return False, 1