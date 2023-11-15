    def forward_request(self, method, path, data, headers):

        modified_data = None

        # If this request contains streaming v4 authentication signatures, strip them from the message
        # Related isse: https://github.com/localstack/localstack/issues/98
        # TODO we should evaluate whether to replace moto s3 with scality/S3:
        # https://github.com/scality/S3/issues/237
        if headers.get('x-amz-content-sha256') == 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD':
            modified_data = strip_chunk_signatures(data)

        # POST requests to S3 may include a "${filename}" placeholder in the
        # key, which should be replaced with an actual file name before storing.
        if method == 'POST':
            original_data = modified_data or data
            expanded_data = expand_multipart_filename(original_data, headers)
            if expanded_data is not original_data:
                modified_data = expanded_data

        # persist this API call to disk
        persistence.record('s3', method, path, data, headers)

        parsed = urlparse.urlparse(path)
        query = parsed.query
        path = parsed.path
        bucket = path.split('/')[1]
        query_map = urlparse.parse_qs(query)
        if query == 'notification' or 'notification' in query_map:
            response = Response()
            response.status_code = 200
            if method == 'GET':
                # TODO check if bucket exists
                result = '<NotificationConfiguration xmlns="%s">' % XMLNS_S3
                if bucket in S3_NOTIFICATIONS:
                    notif = S3_NOTIFICATIONS[bucket]
                    for dest in ['Queue', 'Topic', 'CloudFunction']:
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
                for dest in ['Queue', 'Topic', 'CloudFunction']:
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

            # return response for ?notification request
            return response

        if query == 'cors' or 'cors' in query_map:
            if method == 'GET':
                return get_cors(bucket)
            if method == 'PUT':
                return set_cors(bucket, data)
            if method == 'DELETE':
                return delete_cors(bucket)

        if modified_data:
            return Request(data=modified_data, headers=headers, method=method)
        return True