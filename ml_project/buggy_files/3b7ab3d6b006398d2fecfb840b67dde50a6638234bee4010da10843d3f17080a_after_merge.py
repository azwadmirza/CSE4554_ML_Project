def search(type, hex, string, executable, writable, value, mapping, save, next):
    # Adjust pointer sizes to the local architecture
    if type == 'pointer':
        type = {
            4: 'dword',
            8: 'qword'
        }[pwndbg.arch.ptrsize]

    if save is None:
        save = bool(pwndbg.config.auto_save_search)

    if hex:
        value = codecs.decode(value, 'hex')

    # Convert to an integer if needed, and pack to bytes
    if type not in ('string', 'bytes'):
        value = pwndbg.commands.fix_int(value)
        value &= pwndbg.arch.ptrmask
        fmt = {
            'little': '<',
            'big': '>'
        }[pwndbg.arch.endian] + {
            'byte': 'B',
            'short': 'H',
            'dword': 'L',
            'qword': 'Q'
        }[type]

        value = struct.pack(fmt, value)

    # Null-terminate strings
    elif type == 'string':
        value += b'\x00'

    # Prep the saved set if necessary
    global saved
    if save:
        saved = set()

    # Perform the search
    for address in pwndbg.search.search(value,
                                        mapping=mapping,
                                        executable=executable,
                                        writable=writable):

        if next and address not in saved:
            continue

        if save:
            saved.add(address)

        print_search_hit(address)