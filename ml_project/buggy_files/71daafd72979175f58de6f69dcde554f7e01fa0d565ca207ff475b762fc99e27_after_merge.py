    def return_response(self, method, path, data, headers, response, request_handler):
        if method == 'OPTIONS' and path == '/':
            # Allow CORS preflight requests to succeed.
            return 200

        if method != 'POST':
            return

        region_name = extract_region_from_auth_header(headers)
        req_data = urlparse.parse_qs(to_str(data))
        action = req_data.get('Action', [None])[0]
        content_str = content_str_original = to_str(response.content)

        self._fire_event(req_data, response)

        # patch the response and add missing attributes
        if action == 'GetQueueAttributes':
            content_str = self._add_queue_attributes(path, req_data, content_str, headers)

        # patch the response and return the correct endpoint URLs / ARNs
        if action in ('CreateQueue', 'GetQueueUrl', 'ListQueues', 'GetQueueAttributes'):
            if config.USE_SSL and '<QueueUrl>http://' in content_str:
                # return https://... if we're supposed to use SSL
                content_str = re.sub(r'<QueueUrl>\s*http://', r'<QueueUrl>https://', content_str)
            # expose external hostname:port
            external_port = SQS_PORT_EXTERNAL or get_external_port(headers, request_handler)
            content_str = re.sub(r'<QueueUrl>\s*([a-z]+)://[^<]*:([0-9]+)/([^<]*)\s*</QueueUrl>',
                r'<QueueUrl>\1://%s:%s/\3</QueueUrl>' % (HOSTNAME_EXTERNAL, external_port), content_str)
            # fix queue ARN
            content_str = re.sub(r'<([a-zA-Z0-9]+)>\s*arn:aws:sqs:elasticmq:([^<]+)</([a-zA-Z0-9]+)>',
                r'<\1>arn:aws:sqs:%s:\2</\3>' % (region_name), content_str)

        if content_str_original != content_str:
            # if changes have been made, return patched response
            new_response = Response()
            new_response.status_code = response.status_code
            new_response.headers = response.headers
            new_response._content = content_str
            new_response.headers['content-length'] = len(new_response._content)
            return new_response

        # Since the following 2 API calls are not implemented in ElasticMQ, we're mocking them
        # and letting them to return an empty response
        if action == 'TagQueue':
            new_response = Response()
            new_response.status_code = 200
            new_response._content = ("""
                <?xml version="1.0"?>
                <TagQueueResponse>
                    <ResponseMetadata>
                        <RequestId>{}</RequestId>
                    </ResponseMetadata>
                </TagQueueResponse>
            """).strip().format(uuid.uuid4())
            return new_response
        elif action == 'ListQueueTags':
            new_response = Response()
            new_response.status_code = 200
            new_response._content = ("""
                <?xml version="1.0"?>
                <ListQueueTagsResponse xmlns="{}">
                    <ListQueueTagsResult/>
                    <ResponseMetadata>
                        <RequestId>{}</RequestId>
                    </ResponseMetadata>
                </ListQueueTagsResponse>
            """).strip().format(XMLNS_SQS, uuid.uuid4())
            return new_response