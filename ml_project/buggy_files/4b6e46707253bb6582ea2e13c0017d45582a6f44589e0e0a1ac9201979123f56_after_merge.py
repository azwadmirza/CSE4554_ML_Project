def setup(bot):
    bot.config.define_section('safety', SafetySection)

    if 'safety_cache' not in bot.memory:
        bot.memory['safety_cache'] = tools.SopelMemory()
    if 'safety_cache_lock' not in bot.memory:
        bot.memory['safety_cache_lock'] = threading.Lock()
    for item in bot.config.safety.known_good:
        known_good.append(re.compile(item, re.I))

    old_file = os.path.join(bot.config.homedir, 'malwaredomains.txt')
    if os.path.exists(old_file) and os.path.isfile(old_file):
        LOGGER.info('Removing old malwaredomains file from %s', old_file)
        try:
            os.remove(old_file)
        except Exception as err:
            # for lack of a more specific error type...
            # Python on Windows throws an exception if the file is in use
            LOGGER.info('Could not delete %s: %s', old_file, str(err))

    loc = os.path.join(bot.config.homedir, 'unsafedomains.txt')
    if os.path.isfile(loc):
        if os.path.getmtime(loc) < time.time() - 24 * 60 * 60:
            # File exists but older than one day — update it
            _download_domain_list(loc)
    else:
        _download_domain_list(loc)
    with open(loc, 'r') as f:
        for line in f:
            clean_line = unicode(line).strip().lower()
            if not clean_line or clean_line[0] == '#':
                # blank line or comment
                continue

            parts = clean_line.split(' ', 1)
            try:
                domain = parts[1]
            except IndexError:
                # line does not contain a hosts entry; skip it
                continue

            if '.' in domain:
                # only publicly routable domains matter; skip loopback/link-local stuff
                malware_domains.add(domain)