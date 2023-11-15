def malloc_chunk(addr, fake=False, verbose=False, simple=False):
    """Print a malloc_chunk struct's contents."""
    # points to the real start of the chunk
    cursor = int(addr)

    allocator = pwndbg.heap.current
    ptr_size = allocator.size_sz

    size_field = pwndbg.memory.u(cursor + allocator.chunk_key_offset('size'))
    real_size = size_field & ~allocator.malloc_align_mask

    headers_to_print = []  # both state (free/allocated) and flags
    fields_to_print = set()  # in addition to addr and size
    out_fields = "Addr: {}\n".format(M.get(cursor))

    if fake:
        headers_to_print.append(message.on("Fake chunk"))
        verbose = True  # print all fields for fake chunks

    if simple:
        chunk = read_chunk(cursor)

        if not headers_to_print:
            headers_to_print.append(message.hint(M.get(cursor)))

        prev_inuse, is_mmapped, non_main_arena = allocator.chunk_flags(int(chunk['size']))
        if prev_inuse:
            headers_to_print.append(message.hint('PREV_INUSE'))
        if is_mmapped:
            headers_to_print.append(message.hint('IS_MMAPED'))
        if non_main_arena:
            headers_to_print.append(message.hint('NON_MAIN_ARENA'))

        print(' | '.join(headers_to_print))
        for key, val in chunk.items():
            print(message.system(key) + ": 0x{:02x}".format(int(val)))
        print('')
        return

    arena = allocator.get_arena_for_chunk(cursor)
    arena_address = None
    is_top = False
    if not fake and arena:
        arena_address = arena.address
        top_chunk = arena['top']
        if cursor == top_chunk:
            headers_to_print.append(message.off("Top chunk"))
            is_top = True

    if not is_top:
        fastbins = allocator.fastbins(arena_address) or {}
        smallbins = allocator.smallbins(arena_address) or {}
        largebins = allocator.largebins(arena_address) or {}
        unsortedbin = allocator.unsortedbin(arena_address) or {}
        if allocator.has_tcache():
            tcachebins = allocator.tcachebins(None)

        if real_size in fastbins.keys() and cursor in fastbins[real_size]:
            headers_to_print.append(message.on("Free chunk (fastbins)"))
            if not verbose:
                fields_to_print.add('fd')

        elif real_size in smallbins.keys() and cursor in bin_addrs(smallbins[real_size], "smallbins"):
            headers_to_print.append(message.on("Free chunk (smallbins)"))
            if not verbose:
                fields_to_print.update(['fd', 'bk'])

        elif real_size >= list(largebins.items())[0][0] and cursor in bin_addrs(largebins[(list(largebins.items())[allocator.largebin_index(real_size) - 64][0])], "largebins"):
            headers_to_print.append(message.on("Free chunk (largebins)"))
            if not verbose:
                fields_to_print.update(['fd', 'bk', 'fd_nextsize', 'bk_nextsize'])
        
        elif cursor in bin_addrs(unsortedbin['all'], "unsortedbin"):
            headers_to_print.append(message.on("Free chunk (unsortedbin)"))
            if not verbose:
                fields_to_print.update(['fd', 'bk'])

        elif allocator.has_tcache() and real_size in tcachebins.keys() and cursor + ptr_size*2 in bin_addrs(tcachebins[real_size], "tcachebins"):
            headers_to_print.append(message.on("Free chunk (tcache)"))
            if not verbose:
                fields_to_print.add('fd')

        else:
            headers_to_print.append(message.hint("Allocated chunk"))

    if verbose:
        fields_to_print.update(['prev_size', 'size', 'fd', 'bk', 'fd_nextsize', 'bk_nextsize'])
    else:
        out_fields += "Size: 0x{:02x}\n".format(size_field)

    prev_inuse, is_mmapped, non_main_arena = allocator.chunk_flags(size_field)
    if prev_inuse:
        headers_to_print.append(message.hint('PREV_INUSE'))
    if is_mmapped:
        headers_to_print.append(message.hint('IS_MMAPED'))
    if non_main_arena:
        headers_to_print.append(message.hint('NON_MAIN_ARENA'))

    fields_ordered = ['prev_size', 'size', 'fd', 'bk', 'fd_nextsize', 'bk_nextsize']
    for field_to_print in fields_ordered:
        if field_to_print in fields_to_print:
            out_fields += message.system(field_to_print) + ": 0x{:02x}\n".format(pwndbg.memory.u(cursor + allocator.chunk_key_offset(field_to_print)))

    print(' | '.join(headers_to_print) + "\n" + out_fields)