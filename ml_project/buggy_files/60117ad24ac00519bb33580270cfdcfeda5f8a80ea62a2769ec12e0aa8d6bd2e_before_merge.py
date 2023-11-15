    def _vault_archive_response(self, request, full_url, headers):
        method = request.method
        body = request.body
        parsed_url = urlparse(full_url)
        querystring = parse_qs(parsed_url.query, keep_blank_values=True)
        vault_name = full_url.split("/")[-2]

        if method == 'POST':
            return self._vault_archive_response_post(vault_name, body, querystring, headers)