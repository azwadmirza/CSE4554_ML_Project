def find_fake_fast(addr, size=None):
    """Find candidate fake fast chunks overlapping the specified address."""
    psize = pwndbg.arch.ptrsize
    allocator = pwndbg.heap.current
    align = allocator.malloc_alignment
    min_fast = allocator.min_chunk_size
    max_fast = allocator.global_max_fast
    max_fastbin = allocator.fastbin_index(max_fast)
    start = int(addr) - max_fast + psize
    if start < 0:
        print(message.warn('addr - global_max_fast is negative, if the max_fast is not corrupted, you gave wrong address'))
        start = 0  # TODO, maybe some better way to handle case when global_max_fast is overwritten with something large
    mem = pwndbg.memory.read(start, max_fast - psize, partial=True)

    fmt = {
        'little': '<',
        'big': '>'
    }[pwndbg.arch.endian] + {
        4: 'I',
        8: 'Q'
    }[psize]

    if size is None:
        sizes = range(min_fast, max_fast + 1, align)
    else:
        sizes = [int(size)]

    print(C.banner("FAKE CHUNKS"))
    for size in sizes:
        fastbin  = allocator.fastbin_index(size)
        for offset in range((max_fastbin - fastbin) * align, max_fast - align + 1):
            candidate = mem[offset : offset + psize]
            if len(candidate) == psize:
                value = struct.unpack(fmt, candidate)[0]
                if allocator.fastbin_index(value) == fastbin:
                    malloc_chunk(start+offset-psize, fake=True)