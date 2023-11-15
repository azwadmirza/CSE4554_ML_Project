    def __init__(self, contype=None, databases=None, users=None, source=None, netmask=None,
                 method=None, options=None, line=None):
        '''
        This function can be called with a comma seperated list of databases and a comma seperated
        list of users and it will act as a generator that returns a expanded list of rules one by
        one.
        '''

        super(PgHbaRule, self).__init__()

        if line:
            # Read valies from line if parsed
            self.fromline(line)

        # read rule cols from parsed items
        rule = dict(zip(PG_HBA_HDR, [contype, databases, users, source, netmask, method, options]))
        for key, value in rule.items():
            if value:
                self[key] = value

        # Some sanity checks
        for key in ['method', 'type']:
            if key not in self:
                raise PgHbaRuleError('Missing {0} in rule {1}'.format(key, self))

        if self['method'] not in PG_HBA_METHODS:
            msg = "invalid method {0} (should be one of '{1}')."
            raise PgHbaRuleValueError(msg.format(self['method'], "', '".join(PG_HBA_METHODS)))

        if self['type'] not in PG_HBA_TYPES:
            msg = "invalid connection type {0} (should be one of '{1}')."
            raise PgHbaRuleValueError(msg.format(self['type'], "', '".join(PG_HBA_TYPES)))

        if self['type'] == 'local':
            self.unset('src')
            self.unset('mask')
        elif 'src' not in self:
            raise PgHbaRuleError('Missing src in rule {1}'.format(self))
        elif '/' in self['src']:
            self.unset('mask')
        else:
            self['src'] = str(self.source())
            self.unset('mask')