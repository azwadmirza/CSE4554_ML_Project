    def get_data_from_response(self, response):
        result = {'status_code': str(response.status_code)}

        # Django does not expose a public API to iterate over the headers of a response.
        # Unfortunately, we have to access the private _headers dictionary here, which is
        # a mapping of the form lower-case-header: (Original-Header, value)
        if getattr(response, '_headers', {}):
            result['headers'] = {key: value[1] for key, value in response._headers.items()}
        return result