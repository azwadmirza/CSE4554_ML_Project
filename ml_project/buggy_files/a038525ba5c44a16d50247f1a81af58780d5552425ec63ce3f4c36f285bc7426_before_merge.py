def parse_prometheus(alert, external_url):

    status = alert.get('status', 'firing')

    labels = copy(alert['labels'])
    annotations = copy(alert['annotations'])

    starts_at = parse_date(alert['startsAt'])
    if alert['endsAt'] == '0001-01-01T00:00:00Z':
        ends_at = None
    else:
        ends_at = parse_date(alert['endsAt'])

    if status == 'firing':
        severity = labels.pop('severity', 'warning')
        create_time = starts_at
    elif status == 'resolved':
        severity = 'normal'
        create_time = ends_at
    else:
        severity = 'unknown'
        create_time = ends_at or starts_at

    # get labels
    resource = labels.pop('exported_instance', None) or labels.pop('instance', 'n/a')
    event = labels.pop('alertname')
    environment = labels.pop('environment', 'Production')

    # get annotations
    correlate = annotations.pop('correlate').split(',') if 'correlate' in annotations else None
    service = annotations.pop('service', '').split(',')
    group = annotations.pop('job', 'Prometheus')
    value = annotations.pop('value', None)

    # build alert text
    summary = annotations.pop('summary', None)
    description = annotations.pop('description', None)
    text = description or summary or '%s: %s on %s' % (labels['job'], labels['alertname'], labels['instance'])

    try:
        timeout = int(labels.pop('timeout', 0)) or None
    except ValueError:
        timeout = None

    if external_url:
        annotations['externalUrl'] = external_url
    if 'generatorURL' in alert:
        annotations['moreInfo'] = '<a href="%s" target="_blank">Prometheus Graph</a>' % alert['generatorURL']

    return Alert(
        resource=resource,
        event=event,
        environment=environment,
        severity=severity,
        correlate=correlate,
        service=service,
        group=group,
        value=value,
        text=text,
        attributes=annotations,
        origin='prometheus/' + labels.pop('monitor', '-'),
        event_type='prometheusAlert',
        create_time=create_time.astimezone(tz=pytz.UTC).replace(tzinfo=None),
        timeout=timeout,
        raw_data=alert,
        tags=["%s=%s" % t for t in labels.items()]  # any labels left are used for tags
    )