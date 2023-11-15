    def __init__(self, rule_type, rule_control, rule_path, rule_args=None):
        self._control = None
        self._args = None
        self.rule_type = rule_type
        self.rule_control = rule_control

        self.rule_path = rule_path
        self.rule_args = rule_args