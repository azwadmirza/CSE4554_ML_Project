def _extract_logs_from_span(span):
    if span.time_events is None:
        return None

    logs = []
    for time_event in span.time_events:
        annotation = time_event.annotation
        if not annotation:
            continue

        fields = []
        if annotation.attributes is not None:
            fields = _extract_tags(annotation.attributes.attributes)

        fields.append(jaeger.Tag(
            key='message',
            vType=jaeger.TagType.STRING,
            vStr=annotation.description))

        event_time = datetime.datetime.strptime(
            time_event.timestamp, ISO_DATETIME_REGEX)
        timestamp = calendar.timegm(event_time.timetuple()) * 1000

        logs.append(jaeger.Log(timestamp=timestamp, fields=fields))
    return logs