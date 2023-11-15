def iter_phdrs(ehdr):
    if not ehdr:
        return

    phnum, phentsize, phdr = get_phdrs(ehdr.address)

    if not phdr:
        return

    first_phdr = phdr.address
    PhdrType   = phdr.type

    for i in range(0, phnum):
        p_phdr = int(first_phdr + (i*phentsize))
        p_phdr = read(PhdrType, p_phdr)
        yield p_phdr