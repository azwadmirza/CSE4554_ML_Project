    def __init__(self, _id, dp_id, conf):
        self.rules = []
        self.exact_match = None
        self.meter = False
        self.matches = {}
        self.set_fields = set()
        conf = copy.deepcopy(conf)
        if isinstance(conf, dict):
            rules = conf.get('rules', [])
        elif isinstance(conf, list):
            rules = conf
            conf = {}
        else:
            raise InvalidConfigError(
                'ACL conf is an invalid type %s' % self._id)
        conf['rules'] = []
        for rule in rules:
            test_config_condition(not isinstance(rule, dict), (
                'ACL rule is %s not %s' % (type(rule), dict)))
            conf['rules'].append(rule.get('rule', rule))
        super(ACL, self).__init__(_id, dp_id, conf)