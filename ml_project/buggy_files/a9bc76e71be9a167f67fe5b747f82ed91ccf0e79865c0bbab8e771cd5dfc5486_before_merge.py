def _read_data_chunk(fid, format_tag, channels, bit_depth, is_big_endian,
                     block_align, mmap=False):
    """
    Notes
    -----
    Assumes file pointer is immediately after the 'data' id

    It's possible to not use all available bits in a container, or to store
    samples in a container bigger than necessary, so bytes_per_sample uses
    the actual reported container size (nBlockAlign / nChannels).  Real-world
    examples:

    Adobe Audition's "24-bit packed int (type 1, 20-bit)"

        nChannels = 2, nBlockAlign = 6, wBitsPerSample = 20

    http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-int12-AFsp.wav
    is:

        nChannels = 2, nBlockAlign = 4, wBitsPerSample = 12

    http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Docs/multichaudP.pdf
    gives an example of:

        nChannels = 2, nBlockAlign = 8, wBitsPerSample = 20
    """
    if is_big_endian:
        fmt = '>'
    else:
        fmt = '<'

    # Size of the data subchunk in bytes
    size = struct.unpack(fmt+'I', fid.read(4))[0]

    # Number of bytes per sample (sample container size)
    bytes_per_sample = block_align // channels
    if bit_depth == 8:
        dtype = 'u1'
    else:
        if format_tag == WAVE_FORMAT.PCM:
            dtype = f'{fmt}i{bytes_per_sample}'
        else:
            dtype = f'{fmt}f{bytes_per_sample}'

    if not mmap:
        data = numpy.frombuffer(fid.read(size), dtype=dtype)
    else:
        start = fid.tell()
        data = numpy.memmap(fid, dtype=dtype, mode='c', offset=start,
                            shape=(size//bytes_per_sample,))
        fid.seek(start + size)

    if channels > 1:
        data = data.reshape(-1, channels)
    return data