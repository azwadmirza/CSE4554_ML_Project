def setup(bot):
    bot.config.define_section('safety', SafetySection)

    if 'safety_cache' not in bot.memory:
        bot.memory['safety_cache'] = tools.SopelMemory()
    if 'safety_cache_lock' not in bot.memory:
        bot.memory['safety_cache_lock'] = threading.Lock()
    for item in bot.config.safety.known_good:
        known_good.append(re.compile(item, re.I))

    loc = os.path.join(bot.config.homedir, 'malwaredomains.txt')
    if os.path.isfile(loc):
        if os.path.getmtime(loc) < time.time() - 24 * 60 * 60 * 7:
            # File exists but older than one week — update it
            _download_malwaredomains_db(loc)
    else:
        _download_malwaredomains_db(loc)
    with open(loc, 'r') as f:
        for line in f:
            clean_line = unicode(line).strip().lower()
            if clean_line != '':
                malware_domains.add(clean_line)