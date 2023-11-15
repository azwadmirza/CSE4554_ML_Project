def reverse_readlines(file_path, skip_empty=True, append_newline=False,
                      block_size=128 * 1024, encoding='utf-8'):
    """
    Flexible function for reversing read lines incrementally.

    This code is part of the flyingcircus package: https://pypi.org/project/flyingcircus/
    The code was adapted for our use case.
    All credits go to the original author.

    Args:
        file_path (str): The input file path.
        skip_empty (bool): Skip empty lines.
        append_newline (bool): Append a new line character at the end of each yielded line.
        block_size (int): The block size.
        encoding (str): The encoding for correct block size computation.

    Yields:
        line (str): The next line.

    """
    newline = '\n'
    empty = ''
    remainder = empty
    block_generator = blocks_r
    for block in block_generator(file_path, size=block_size):
        lines = block.split(b'\n')
        if remainder:
            lines[-1] = lines[-1] + remainder
        remainder = lines[0]
        mask = slice(-1, 0, -1)
        for line in lines[mask]:
            if line or not skip_empty:
                yield line.decode(encoding) + (newline if append_newline else empty)
    if remainder or not skip_empty:
        yield remainder.decode(encoding) + (newline if append_newline else empty)