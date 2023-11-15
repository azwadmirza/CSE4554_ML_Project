def blocks_r(file_path, size=64 * 1024):
    """
    Yields the data within a file in reverse-ordered blocks of given size.

    This code is part of the flyingcircus package: https://pypi.org/project/flyingcircus/
    The code was adapted for our use case.
    All credits go to the original author.

    Note that:
     - the content of the block is NOT reversed.

    Args:
        file_path (str): The input file path.
        size (int): The block size.

    Yields:
        block (bytes): The data within the blocks.

    """
    with io.open(file_path, 'rb') as file_obj:
        remaining_size = file_obj.seek(0, os.SEEK_END)
        while remaining_size > 0:
            block_size = min(remaining_size, size)
            file_obj.seek(remaining_size - block_size)
            block = file_obj.read(block_size)
            remaining_size -= block_size
            yield block