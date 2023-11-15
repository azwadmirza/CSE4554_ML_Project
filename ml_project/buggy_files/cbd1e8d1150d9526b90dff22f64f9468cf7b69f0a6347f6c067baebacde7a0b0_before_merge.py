def reverse_readlines(filename, buf_size=2097152, encoding=default_encoding):
    """A generator that returns the lines of a file in reverse order.

    Thanks to Andomar: http://stackoverflow.com/a/23646049

    :param filename:
    :type filename: str
    :param encoding:
    :type encoding: str
    :param buf_size:
    :return:
    :rtype: collections.Iterable of str
    """
    new_line = '\n'
    with io.open(filename, 'rb') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buf = fh.read(min(remaining_size, buf_size))
            buf = text_type(buf.decode(sys.getfilesystemencoding()) if os.name == 'nt' else buf, errors='replace')
            remaining_size -= buf_size
            lines = buf.split(new_line)
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concact the segment to the last line of new chunk
                # instead, yield the segment first
                if buf[-1] is not new_line:
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if len(lines[index]):
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment