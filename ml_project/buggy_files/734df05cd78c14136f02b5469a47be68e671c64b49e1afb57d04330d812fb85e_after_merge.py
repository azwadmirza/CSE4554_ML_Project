    def match(self, context, variables1, variables2):
        def matches(part, variables):
            return all(var[1] == 100 and var[0] in variables
                       or variables.get(var[0], -1) == var[1] for var in part)

        if (variables1, variables2) == (context.variables1, context.variables2):
            return self.PERFECT_MATCH

        if "attr_pairs" in context.values:
            left, right = zip(*context.values["attr_pairs"])
            if matches(left, variables1) and matches(right, variables2):
                return 0.5

        return self.NO_MATCH