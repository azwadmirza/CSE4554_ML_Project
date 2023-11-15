    def forward_request(self, method, path, data, headers):
        if method == 'OPTIONS':
            return 200

        # kill the process if we receive this header
        headers.get(HEADER_KILL_SIGNAL) and os._exit(0)

        target = headers.get('x-amz-target', '')
        auth_header = headers.get('authorization', '')
        host = headers.get('host', '')
        headers[HEADER_LOCALSTACK_EDGE_URL] = 'https://%s' % host

        # extract API details
        api, port, path, host = get_api_from_headers(headers, path)

        if port and int(port) < 0:
            return 404

        if not port:
            port = get_port_from_custom_rules(method, path, data, headers) or port

        if not port:
            if api in ['', None, '_unknown_']:
                truncated = truncate(data)
                LOG.info(('Unable to find forwarding rule for host "%s", path "%s", '
                    'target header "%s", auth header "%s", data "%s"') % (host, path, target, auth_header, truncated))
            else:
                LOG.info(('Unable to determine forwarding port for API "%s" - please '
                    'make sure this API is enabled via the SERVICES configuration') % api)
            response = Response()
            response.status_code = 404
            response._content = '{"status": "running"}'
            return response

        use_ssl = config.USE_SSL

        connect_host = '%s:%s' % (config.HOSTNAME, port)
        url = 'http%s://%s%s' % ('s' if use_ssl else '', connect_host, path)
        headers['Host'] = host
        function = getattr(requests, method.lower())
        if isinstance(data, dict):
            data = json.dumps(data)

        response = function(url, data=data, headers=headers, verify=False)
        return response