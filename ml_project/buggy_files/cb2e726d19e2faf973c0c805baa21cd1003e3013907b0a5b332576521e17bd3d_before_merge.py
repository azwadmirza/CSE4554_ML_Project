def get_containing_segments(elf_filepath, elf_loadaddr, vaddr):
    elf = get_elf_info_rebased(elf_filepath, elf_loadaddr)
    segments = []
    for seg in elf.segments:
        # disregard non-LOAD segments that are not file-backed (typically STACK)
        if 'LOAD' not in seg['p_type'] and seg['p_filesz'] == 0:
            continue
        # disregard segments not containing vaddr
        if vaddr < seg['p_vaddr'] or vaddr >= seg['x_vaddr_mem_end']:
            continue
        segments.append(dict(seg))
    return segments