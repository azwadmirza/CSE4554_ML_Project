    def forward_request(self, method, path, data, headers):

        if re.match(PATH_REGEX_USER_REQUEST, path):
            search_match = re.search(PATH_REGEX_USER_REQUEST, path)
            api_id = search_match.group(1)
            stage = search_match.group(2)
            relative_path_w_query_params = '/%s' % search_match.group(3)
            return invoke_rest_api(api_id, stage, method, relative_path_w_query_params, data, headers, path=path)

        data = data and json.loads(to_str(data))

        if re.match(PATH_REGEX_AUTHORIZERS, path):
            return handle_authorizers(method, path, data, headers)

        if re.match(PATH_REGEX_RESPONSES, path):
            search_match = re.search(PATH_REGEX_RESPONSES, path)
            api_id = search_match.group(1)
            if method == 'GET':
                return get_gateway_responses(api_id)
            if method == 'PUT':
                response_type = search_match.group(2).lstrip('/')
                return put_gateway_response(api_id, response_type, data)

        return True