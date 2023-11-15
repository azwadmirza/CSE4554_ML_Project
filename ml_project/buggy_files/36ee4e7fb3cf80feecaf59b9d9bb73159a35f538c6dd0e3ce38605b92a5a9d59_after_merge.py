    def num_violations(self, rules=None, types=None):
        """Count the number of violations.

        Optionally now with filters.
        """
        violations = self.violations
        if types:
            try:
                types = tuple(types)
            except TypeError:
                types = (types,)
            violations = [v for v in violations if isinstance(v, types)]
        if rules:
            if isinstance(rules, str):
                rules = (rules,)
            else:
                rules = tuple(rules)
            violations = [v for v in violations if v.rule_code() in rules]
        return len(violations)