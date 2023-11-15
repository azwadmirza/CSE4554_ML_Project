def update_s3(method, path, data, headers, response=None, return_forward_info=False):

    if return_forward_info:

        modified_data = None

        # If this request contains streaming v4 authentication signatures, strip them from the message
        # Related isse: https://github.com/atlassian/localstack/issues/98
        # TODO we should evaluate whether to replace moto s3 with scality/S3:
        # https://github.com/scality/S3/issues/237
        if headers.get('x-amz-content-sha256') == 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD':
            modified_data = strip_chunk_signatures(data)

        # persist this API call to disk
        persistence.record('s3', method, path, data, headers)

        parsed = urlparse.urlparse(path)
        query = parsed.query
        path = parsed.path
        bucket = path.split('/')[1]
        query_map = urlparse.parse_qs(query)
        if method == 'PUT' and (query == 'notification' or 'notification' in query_map):
            tree = ET.fromstring(data)
            queue_config = tree.find('{%s}QueueConfiguration' % XMLNS_S3)
            if len(queue_config):
                S3_NOTIFICATIONS[bucket] = {
                    'Id': get_xml_text(queue_config, 'Id'),
                    'Event': get_xml_text(queue_config, 'Event', ns=XMLNS_S3),
                    'Queue': get_xml_text(queue_config, 'Queue', ns=XMLNS_S3),
                    'Topic': get_xml_text(queue_config, 'Topic', ns=XMLNS_S3),
                    'CloudFunction': get_xml_text(queue_config, 'CloudFunction', ns=XMLNS_S3)
                }
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

    # get subscribers and send bucket notifications
    if method in ('PUT', 'DELETE') and '/' in path[1:]:
        parts = path[1:].split('/', 1)
        bucket_name = parts[0]
        object_path = '/%s' % parts[1]
        send_notifications(method, bucket_name, object_path)
    # append CORS headers to response
    if response:
        parsed = urlparse.urlparse(path)
        bucket_name = parsed.path.split('/')[0]
        append_cors_headers(bucket_name, request_method=method, request_headers=headers, response=response)