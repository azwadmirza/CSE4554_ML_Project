def handle_notification_request(bucket, method, data):
    response = Response()
    response.status_code = 200
    response._content = ''
    if method == 'GET':
        # TODO check if bucket exists
        result = '<NotificationConfiguration xmlns="%s">' % XMLNS_S3
        if bucket in S3_NOTIFICATIONS:
            notif = S3_NOTIFICATIONS[bucket]
            for dest in NOTIFICATION_DESTINATION_TYPES:
                if dest in notif:
                    dest_dict = {
                        '%sConfiguration' % dest: {
                            'Id': uuid.uuid4(),
                            dest: notif[dest],
                            'Event': notif['Event'],
                            'Filter': notif['Filter']
                        }
                    }
                    result += xmltodict.unparse(dest_dict, full_document=False)
        result += '</NotificationConfiguration>'
        response._content = result

    if method == 'PUT':
        parsed = xmltodict.parse(data)
        notif_config = parsed.get('NotificationConfiguration')
        S3_NOTIFICATIONS.pop(bucket, None)
        for dest in NOTIFICATION_DESTINATION_TYPES:
            config = notif_config.get('%sConfiguration' % (dest))
            if config:
                events = config.get('Event')
                if isinstance(events, six.string_types):
                    events = [events]
                event_filter = config.get('Filter', {})
                # make sure FilterRule is an array
                s3_filter = _get_s3_filter(event_filter)
                if s3_filter and not isinstance(s3_filter.get('FilterRule', []), list):
                    s3_filter['FilterRule'] = [s3_filter['FilterRule']]
                # create final details dict
                notification_details = {
                    'Id': config.get('Id'),
                    'Event': events,
                    dest: config.get(dest),
                    'Filter': event_filter
                }
                # TODO: what if we have multiple destinations - would we overwrite the config?
                S3_NOTIFICATIONS[bucket] = clone(notification_details)
    return response