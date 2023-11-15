def fetch():
    retval = {}
    content = retrieve_content(__url__)

    if __check__ in content:
        for match in re.finditer(r"(\d+\.\d+\.\d+\.\d+)/(\d+)", content):
            prefix, mask = match.groups()
            mask = int(mask)
            if MIN_BLACKLIST_MASK <= mask <= MAX_BLACKLIST_MASK:
                start_int = addr_to_int(prefix) & make_mask(mask)
                end_int = start_int | ((1 << 32 - mask) - 1)
                for address in xrange(start_int, end_int + 1):
                    retval[int_to_addr(address)] = (__info__, __reference__)

    return retval