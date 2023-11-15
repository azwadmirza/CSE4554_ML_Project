def reverse_readlines(filename, skip_empty=True, append_newline=False, block_size=512 * 1024,
                      reset_offset=True, encoding='utf-8'):
    """
    Flexible function for reversing read lines incrementally.

    This code is part of the flyingcircus package: https://pypi.org/project/flyingcircus/
    The code was adapted for our use case.
    All credits go to the original author.

    Args:
        filename (str): The input file name.
        skip_empty (bool): Skip empty lines.
        append_newline (bool):
        block_size (int|None): The block size.
            If int, the file is processed in blocks of the specified size.
            If None, the file is processed at once.
        reset_offset (bool): Reset the file offset.
            If True, starts reading from the end of the file.
            Otherwise, starts reading from where the file current position is.
        encoding (str|None): The encoding for correct block size computation.
            If `str`, must be a valid string encoding.
            If None, the default encoding is used.

    Yields:
        line (str): The next line.

    """
    newline = '\n'
    empty = ''
    remainder = empty
    block_generator_kws = dict(size=block_size, reset_offset=reset_offset,
                               encoding=encoding)
    block_generator = blocks_r
    for block in block_generator(filename, **block_generator_kws):
        lines = block.split(newline)
        if remainder:
            lines[-1] = lines[-1] + remainder
        remainder = lines[0]
        mask = slice(-1, 0, -1)
        for line in lines[mask]:
            if line or not skip_empty:
                yield line + (newline if append_newline else empty)
    if remainder or not skip_empty:
        yield remainder + (newline if append_newline else empty)