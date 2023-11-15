def get_scheduled_rule_func(data):
    def func(*args):
        rule_name = data.get('Name')
        client = aws_stack.connect_to_service('events')
        targets = client.list_targets_by_rule(Rule=rule_name)['Targets']
        if targets:
            LOG.debug('Notifying %s targets in response to triggered Events rule %s' % (len(targets), rule_name))
        for target in targets:
            arn = target.get('Arn')
            event = json.loads(target.get('Input') or '{}')
            attr = aws_stack.get_events_target_attributes(target)
            aws_stack.send_event_to_target(arn, event, target_attributes=attr)
    return func