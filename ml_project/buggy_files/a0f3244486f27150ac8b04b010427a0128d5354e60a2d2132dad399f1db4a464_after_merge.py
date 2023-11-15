    def get_languages(self):
        verb, url = KITE_ENDPOINTS.LANGUAGES_ENDPOINT
        success, response = self.perform_http_request(verb, url)
        if response is None or isinstance(response, TEXT_TYPES):
            response = ['python']
        return response