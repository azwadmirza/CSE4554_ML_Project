    def __init__(self, _id, dp_id, conf):
        self.rules = []
        self.exact_match = None
        self.meter = False
        self.matches = {}
        self.set_fields = set()
        for match_fields in (MATCH_FIELDS, OLD_MATCH_FIELDS):
            self.rule_types.update({match: (str, int) for match in match_fields.keys()})
        conf = copy.deepcopy(conf)
        if isinstance(conf, dict):
            rules = conf.get('rules', [])
        elif isinstance(conf, list):
            rules = conf
            conf = {}
        else:
            raise InvalidConfigError(
                'ACL conf is an invalid type %s' % _id)
        conf['rules'] = []
        for rule in rules:
            normalized_rule = rule
            if isinstance(rule, dict):
                normalized_rule = rule.get('rule', rule)
                if normalized_rule is None:
                    normalized_rule = {k: v for k, v in rule.items() if v is not None}
            test_config_condition(not isinstance(normalized_rule, dict), (
                'ACL rule is %s not %s (%s)' % (type(normalized_rule), dict, rules)))
            conf['rules'].append(normalized_rule)
        super(ACL, self).__init__(_id, dp_id, conf)