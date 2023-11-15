def parse_grafana(alert: JSON, match: Dict[str, Any], args: ImmutableMultiDict) -> Alert:
    alerting_severity = args.get('severity', 'major')

    if alert['state'] == 'alerting':
        severity = alerting_severity
    elif alert['state'] == 'ok':
        severity = 'normal'
    else:
        severity = 'indeterminate'

    environment = args.get('environment', 'Production')  # TODO: verify at create?
    event_type = args.get('event_type', 'performanceAlert')
    group = args.get('group', 'Performance')
    origin = args.get('origin', 'Grafana')
    service = args.get('service', 'Grafana')
    timeout = args.get('timeout', type=int)

    attributes = match.get('tags', None) or dict()
    attributes = {k.replace('.', '_'): v for (k, v) in attributes.items()}

    attributes['ruleId'] = str(alert['ruleId'])
    if 'ruleUrl' in alert:
        attributes['ruleUrl'] = '<a href="%s" target="_blank">Rule</a>' % alert['ruleUrl']
    if 'imageUrl' in alert:
        attributes['imageUrl'] = '<a href="%s" target="_blank">Image</a>' % alert['imageUrl']

    return Alert(
        resource=match['metric'],
        event=alert['ruleName'],
        environment=environment,
        severity=severity,
        service=[service],
        group=group,
        value='%s' % match['value'],
        text=alert.get('message', None) or alert.get('title', alert['state']),
        tags=list(),
        attributes=attributes,
        origin=origin,
        event_type=event_type,
        timeout=timeout,
        raw_data=json.dumps(alert)
    )