def blocks_r(filename, size=64 * 1024, reset_offset=True, encoding='utf-8'):
    """
    Yields the data within a file in reverse-ordered blocks of given size.

    This code is part of the flyingcircus package: https://pypi.org/project/flyingcircus/
    The code was adapted for our use case.
    All credits go to the original author.

    Note that:
     - the content of the block is NOT reversed.

    Args:
        filename (str): The input file name.
        size (int|None): The block size.
            If int, the file is yielded in blocks of the specified size.
            If None, the file is yielded at once.
        reset_offset (bool): Reset the file offset.
            If True, starts reading from the end of the file.
            Otherwise, starts reading from where the file current position is.
        encoding (str|None): The encoding for correct block size computation.
            If `str`, must be a valid string encoding.
            If None, the default encoding is used.

    Yields:
        block (str): The data within the blocks.

    """
    with io.open(filename, 'r', encoding=encoding) as file_obj:
        offset = 0
        if reset_offset:
            file_size = remaining_size = file_obj.seek(0, os.SEEK_END)
        else:
            file_size = remaining_size = file_obj.tell()
        rounding = 0
        while remaining_size > 0:
            offset = min(file_size, offset + size)
            file_obj.seek(file_size - offset)
            block = file_obj.read(min(remaining_size, size))
            remaining_size -= size
            yield block[:len(block) + rounding] if rounding else block