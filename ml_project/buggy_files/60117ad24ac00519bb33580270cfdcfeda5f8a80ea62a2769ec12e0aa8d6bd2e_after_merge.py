    def _vault_archive_response(self, request, full_url, headers):
        method = request.method
        if hasattr(request, 'body'):
            body = request.body
        else:
            body = request.data
        description = ""
        if 'x-amz-archive-description' in request.headers:
            description = request.headers['x-amz-archive-description']
        parsed_url = urlparse(full_url)
        querystring = parse_qs(parsed_url.query, keep_blank_values=True)
        vault_name = full_url.split("/")[-2]

        if method == 'POST':
            return self._vault_archive_response_post(vault_name, body, description, querystring, headers)
        else:
            return 400, headers, "400 Bad Request"