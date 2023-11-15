def file_smart_open(fname, mode='rb', encoding=None):
    """
    Stream from/to local filesystem, transparently (de)compressing gzip and bz2
    files if necessary.

    :arg str fname: The path to the file to open.
    :arg str mode: The mode in which to open the file.
    :arg str encoding: The text encoding to use.
    :returns: A file object
    """
    #
    # This is how we get from the filename to the end result.
    # Decompression is optional, but it always accepts bytes and returns bytes.
    # Decoding is also optional, accepts bytes and returns text.
    # The diagram below is for reading, for writing, the flow is from right to
    # left, but the code is identical.
    #
    #           open as binary         decompress?          decode?
    # filename ---------------> bytes -------------> bytes ---------> text
    #                          raw_fobj        decompressed_fobj   decoded_fobj
    #
    try:  # TODO need to fix this place (for cases with r+ and so on)
        raw_mode = {'r': 'rb', 'w': 'wb', 'a': 'ab'}[mode]
    except KeyError:
        raw_mode = mode
    raw_fobj = open(fname, raw_mode)
    decompressed_fobj = compression_wrapper(raw_fobj, fname, raw_mode)
    decoded_fobj = encoding_wrapper(decompressed_fobj, mode, encoding=encoding)
    return decoded_fobj