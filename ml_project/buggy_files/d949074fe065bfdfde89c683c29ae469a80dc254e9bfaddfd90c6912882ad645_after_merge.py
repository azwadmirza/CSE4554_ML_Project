    def __init__(self, configs=None, overrides=None):
        self._overrides = overrides  # We only store this for child configs
        defaults = ConfigLoader.get_global().load_default_config_file()
        self._configs = nested_combine(
            defaults,
            configs or {'core': {}},
            {'core': overrides or {}})
        # Some configs require special treatment
        self._configs['core']['color'] = False if self._configs['core'].get('nocolor', False) else None
        # Whitelists and blacklists
        if self._configs['core'].get('rules', None):
            self._configs['core']['rule_whitelist'] = self._configs['core']['rules'].split(',')
        else:
            self._configs['core']['rule_whitelist'] = None
        if self._configs['core'].get('exclude_rules', None):
            self._configs['core']['rule_blacklist'] = self._configs['core']['exclude_rules'].split(',')
        else:
            self._configs['core']['rule_blacklist'] = None
        # Configure Recursion
        if self._configs['core'].get('recurse', 0) == 0:
            self._configs['core']['recurse'] = True
        # Dialect and Template selection
        self._configs['core']['dialect_obj'] = dialect_selector(self._configs['core']['dialect'])
        self._configs['core']['templater_obj'] = templater_selector(self._configs['core']['templater'])