    def http_get(self, path, query_data={}, streamed=False, raw=False,
                 **kwargs):
        """Make a GET request to the Gitlab server.

        Args:
            path (str): Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data (dict): Data to send as query parameters
            streamed (bool): Whether the data should be streamed
            raw (bool): If True do not try to parse the output as json
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.

        Raises:
            GitlabHttpError: When the return code is not 2xx
            GitlabParsingError: If the json data could not be parsed
        """
        result = self.http_request('get', path, query_data=query_data,
                                   streamed=streamed, **kwargs)

        if (result.headers['Content-Type'] == 'application/json'
           and not streamed
           and not raw):
            try:
                return result.json()
            except Exception:
                raise GitlabParsingError(
                    error_message="Failed to parse the server message")
        else:
            return result