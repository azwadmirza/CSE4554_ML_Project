    def py_parse_hypermap(self, index=None, downsample=1, cutoff_at_channel=None,  # noqa
                          description=False):
        """Unpack the Delphi/Bruker binary spectral map and return
        numpy array in memory efficient way using pure python implementation.
        (Slow!)

        The function is long and complicated because Delphi/Bruker array
        packing is complicated. Whole parsing is done in one function/method
        to reduce overhead from python function calls. For cleaner parsing
        logic check out fast cython implementation at
        hyperspy/io_plugins/unbcf_fast.pyx

        The method is only meant to be used if for some
        reason c (generated with cython) version of the parser is not compiled.

        Arguments:
        ---------
        index -- the index of hypermap in bcf if there is more than one
            hyper map in file.
        downsample -- downsampling factor (integer). Diferently than
            block_reduce from skimage.measure, the parser populates
            reduced array by suming results of pixels, thus having lower
            memory requiriments. (default 1)
        cutoff_at_kV -- value in keV to truncate the array at. Helps reducing
          size of array. (default None)

        Returns:
        ---------
        numpy array of bruker hypermap, with (y,x,E) shape.
        """
        if index is None:
            index = self.def_index
        # dict of nibbles to struct notation for reading:
        st = {1: 'B', 2: 'B', 4: 'H', 8: 'I', 16: 'Q'}
        spectrum_file = self.get_file('EDSDatabase/SpectrumData' + str(index))
        iter_data, size_chnk = spectrum_file.get_iter_and_properties()[:2]
        if isinstance(cutoff_at_channel, int):
            max_chan = cutoff_at_channel
        else:
            max_chan = self.header.estimate_map_channels(index=index)
        depth = self.header.estimate_map_depth(index=index,
                                               downsample=downsample,
                                               for_numpy=True)
        buffer1 = next(iter_data)
        height, width = strct_unp('<ii', buffer1[:8])
        dwn_factor = downsample
        shape = (-(-height // dwn_factor), -(-width // dwn_factor), max_chan)
        if description:
            return shape, depth
        # hyper map as very flat array:
        vfa = np.zeros(shape[0] * shape[1] * shape[2], dtype=depth)
        offset = 0x1A0
        size = size_chnk
        for line_cnt in range(height):
            if (offset + 4) >= size:
                size = size_chnk + size - offset
                buffer1 = buffer1[offset:] + next(iter_data)
                offset = 0
            line_head = strct_unp('<i', buffer1[offset:offset + 4])[0]
            offset += 4
            for dummy1 in range(line_head):
                if (offset + 22) >= size:
                    size = size_chnk + size - offset
                    buffer1 = buffer1[offset:] + next(iter_data)
                    offset = 0
                # the pixel header contains such information:
                # x index of pixel (uint32);
                # number of channels for whole mapping (unit16);
                # number of channels for pixel (uint16);
                # dummy placehollder (same value in every known bcf) (32bit);
                # flag distinguishing packing data type (16bit):
                #    0 - 16bit packed pulses, 1 - 12bit packed pulses,
                #    >1 - instructively packed spectra;
                # value which sometimes shows the size of packed data (uint16);
                # number of pulses if pulse data are present (uint16) or
                #      additional pulses to the instructively packed data;
                # packed data size (32bit) (without additional pulses)
                #       next header is after that amount of bytes;
                x_pix, chan1, chan2, dummy1, flag, dummy_size1, n_of_pulses,\
                    data_size2 = strct_unp('<IHHIHHHI',
                                           buffer1[offset:offset + 22])
                pix_idx = (x_pix // dwn_factor) + ((-(-width // dwn_factor)) *
                                                   (line_cnt // dwn_factor))
                offset += 22
                if (offset + data_size2) >= size:
                    buffer1 = buffer1[offset:] + next(iter_data)
                    size = size_chnk + size - offset
                    offset = 0
                if flag == 0:
                    data1 = buffer1[offset:offset + data_size2]
                    arr16 = np.fromstring(data1, dtype=np.uint16)
                    pixel = np.bincount(arr16, minlength=chan1 - 1)
                    offset += data_size2
                elif flag == 1:  # and (chan1 != chan2)
                    # Unpack packed 12-bit data to 16-bit uints:
                    data1 = buffer1[offset:offset + data_size2]
                    switched_i2 = np.fromstring(data1,
                                                dtype='<u2'
                                                ).byteswap(True)
                    data2 = np.fromstring(switched_i2.tostring(),
                                          dtype=np.uint8
                                          ).repeat(2)
                    mask = np.ones_like(data2, dtype=bool)
                    mask[0::6] = mask[5::6] = False
                    # Reinterpret expanded as 16-bit:
                    # string representation of array after switch will have
                    # always BE independently from endianess of machine
                    exp16 = np.fromstring(data2[mask].tostring(),
                                          dtype='>u2', count=n_of_pulses)
                    exp16[0::2] >>= 4           # Shift every second short by 4
                    exp16 &= np.uint16(0x0FFF)  # Mask all shorts to 12bit
                    pixel = np.bincount(exp16, minlength=chan1 - 1)
                    offset += data_size2
                else:  # flag > 1
                    # Unpack instructively packed data to pixel channels:
                    pixel = []
                    the_end = offset + data_size2 - 4
                    while offset < the_end:
                        # this would work on py3
                        #size_p, channels = buffer1[offset:offset + 2]
                        # this is needed on py2:
                        size_p, channels = strct_unp('<BB',
                                                     buffer1[offset:offset + 2])
                        offset += 2
                        if size_p == 0:
                            pixel += channels * [0]
                        else:
                            gain = strct_unp('<' + st[size_p * 2],
                                             buffer1[offset:offset + size_p])[0]
                            offset += size_p
                            if size_p == 1:
                                # special case with nibble switching
                                length = -(-channels // 2)  # integer roof
                                # valid py3 code
                                #a = list(buffer1[offset:offset + length])
                                # this have to be used on py2:
                                a = strct_unp('<' + 'B' * length,
                                              buffer1[offset:offset + length])
                                g = []
                                for i in a:
                                    g += (i & 0x0F) + gain, (i >> 4) + gain
                                pixel += g[:channels]
                            else:
                                length = int(channels * size_p / 2)
                                temp = strct_unp('<' + channels * st[size_p],
                                                 buffer1[offset:offset + length])
                                pixel += [l + gain for l in temp]
                            offset += length
                    if chan2 < chan1:
                        rest = chan1 - chan2
                        pixel += rest * [0]
                    # additional data size:
                    if n_of_pulses > 0:
                        add_s = strct_unp('<I', buffer1[offset:offset + 4])[0]
                        offset += 4
                        if (offset + add_s) >= size:
                            buffer1 = buffer1[offset:] + next(iter_data)
                            size = size_chnk + size - offset
                            offset = 0
                        # the additional pulses:
                        add_pulses = strct_unp('<' + 'H' * n_of_pulses,
                                               buffer1[offset:offset + add_s])
                        offset += add_s
                        for i in add_pulses:
                            pixel[i] += 1
                    else:
                        offset += 4
                # if no downsampling is needed, or if it is first
                # pixel encountered with downsampling on, then
                # use assigment, which is ~4 times faster, than inplace add
                if max_chan < chan1:  # if pixel have more channels than we need
                    chan1 = max_chan
                if (dwn_factor == 1):
                    vfa[max_chan * pix_idx:chan1 + max_chan * pix_idx] =\
                        pixel[:chan1]
                else:
                    vfa[max_chan * pix_idx:chan1 + max_chan * pix_idx] +=\
                        pixel[:chan1]
        vfa.resize((-(-height // dwn_factor),
                    -(-width // dwn_factor),
                    max_chan))
        # check if array is signed, and convert to unsigned
        if str(vfa.dtype)[0] == 'i':
            new_dtype = ''.join(['u', str(vfa.dtype)])
            vfa.dtype = new_dtype
        return vfa