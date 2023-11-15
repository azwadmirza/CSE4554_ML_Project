def matches(event, *rules):
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
        if not re.search(rule, event[name]):
            return False

    return True