    def get_rules(self, with_lines=False):
        '''
        This method returns all the rules of the PgHba object
        '''
        rules = sorted(self.rules.values(),
                       key=lambda rule: rule.weight(self.order,
                                                    len(self.users) + 1,
                                                    len(self.databases) + 1),
                       reverse=True)
        for rule in rules:
            ret = {}
            for key, value in rule.items():
                ret[key] = value
            if not with_lines:
                if 'line' in ret:
                    del ret['line']
            else:
                ret['line'] = rule.line()

            yield ret