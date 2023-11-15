def get_id():
    '''
    Guess the id of the minion.

    - Check /etc/hostname for a value other than localhost
    - If socket.getfqdn() returns us something other than localhost, use it
    - Check /etc/hosts for something that isn't localhost that maps to 127.*
    - Look for a routeable / public IP
    - A private IP is better than a loopback IP
    - localhost may be better than killing the minion

    Returns two values: the detected ID, and a boolean value noting whether or
    not an IP address is being used for the ID.
    '''

    log.debug(
        'Guessing ID. The id can be explicitly in set {0}'.format(
            os.path.join(syspaths.CONFIG_DIR, 'minion')
        )
    )

    # Check /etc/hostname
    try:
        with salt.utils.fopen('/etc/hostname') as hfl:
            name = hfl.read().strip()
        if re.search(r'\s', name):
            log.warning('Whitespace character detected in /etc/hostname. '
                        'This file should not contain any whitespace.')
        else:
            if name != 'localhost':
                return name, False
    except Exception:
        pass

    # Nothing in /etc/hostname or /etc/hostname not found
    fqdn = socket.getfqdn()
    if fqdn != 'localhost':
        log.info('Found minion id from getfqdn(): {0}'.format(fqdn))
        return fqdn, False

    # Can /etc/hosts help us?
    try:
        with salt.utils.fopen('/etc/hosts') as hfl:
            for line in hfl:
                names = line.split()
                ip_ = names.pop(0)
                if ip_.startswith('127.'):
                    for name in names:
                        if name != 'localhost':
                            log.info('Found minion id in hosts file: {0}'
                                     .format(name))
                            return name, False
    except Exception:
        pass

    # Can Windows 'hosts' file help?
    try:
        windir = os.getenv("WINDIR")
        with salt.utils.fopen(windir + '\\system32\\drivers\\etc\\hosts') as hfl:
            for line in hfl:
                # skip commented or blank lines
                if line[0] == '#' or len(line) <= 1:
                    continue
                # process lines looking for '127.' in first column
                try:
                    entry = line.split()
                    if entry[0].startswith('127.'):
                        for name in entry[1:]:  # try each name in the row
                            if name != 'localhost':
                                log.info('Found minion id in hosts file: {0}'.format(name))
                                return name, False
                except IndexError:
                    pass  # could not split line (malformed entry?)
    except Exception:
        pass

    # What IP addresses do we have?
    ip_addresses = [salt.utils.network.IPv4Address(addr) for addr
                    in salt.utils.network.ip_addrs(include_loopback=True)
                    if not addr.startswith('127.')]

    for addr in ip_addresses:
        if not addr.is_private:
            log.info('Using public ip address for id: {0}'.format(addr))
            return str(addr), True

    if ip_addresses:
        addr = ip_addresses.pop(0)
        log.info('Using private ip address for id: {0}'.format(addr))
        return str(addr), True

    log.error('No id found, falling back to localhost')
    return 'localhost', False