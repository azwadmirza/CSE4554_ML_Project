def use_info_auxv():
    lines = pwndbg.info.auxv().splitlines()

    if not lines:
        return None

    auxv = AUXV()
    for line in lines:
        match = re.match('([0-9]+) .*? (0x[0-9a-f]+|[0-9]+)', line)
        if not match:
            print("Warning: Skipping auxv entry '{}'".format(line))
            continue

        const, value = int(match.group(1)), int(match.group(2), 0)
        auxv.set(const, value)

    return auxv