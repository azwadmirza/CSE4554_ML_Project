    def matches(self, identifiers, event, *rules):
        condition = {}
        for rule in rules:
            condition.update(rule)

        for name, rule in condition.items():
            # empty string means non-existant field
            if rule == '':
                if name in event:
                    return False
                else:
                    continue
            if name not in event:
                return False
            if not isinstance(rule, type(event[name])):
                self.logger.warn("Type of rule ({!r}) and data ({!r}) do not "
                                 "match in {!s}, {}!".format(type(rule),
                                                             type(event[name]),
                                                             identifiers,
                                                             name))
            if not isinstance(event[name], str):  # int, float, etc
                return event[name] == rule
            else:
                if not re.search(rule, event[name]):
                    return False

        return True