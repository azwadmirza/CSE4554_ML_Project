    def check_config(self):
        test_config_condition(
            not self.rules, 'no rules found for ACL %s' % self._id)
        for match_fields in (MATCH_FIELDS, OLD_MATCH_FIELDS):
            for match in match_fields.keys():
                self.rule_types[match] = (str, int)
        for rule in self.rules:
            self._check_conf_types(rule, self.rule_types)
            for rule_field, rule_conf in rule.items():
                if rule_field == 'cookie':
                    test_config_condition(rule_conf < 0 or rule_conf > 2**16, (
                        'rule cookie value must be 0-2**16'))
                elif rule_field == 'actions':
                    test_config_condition(
                        not rule_conf,
                        'Missing rule actions in ACL %s' % self._id
                        )
                    self._check_conf_types(rule_conf, self.actions_types)
                    for action_name, action_conf in rule_conf.items():
                        if action_name == 'output':
                            self._check_conf_types(
                                action_conf, self.output_actions_types)