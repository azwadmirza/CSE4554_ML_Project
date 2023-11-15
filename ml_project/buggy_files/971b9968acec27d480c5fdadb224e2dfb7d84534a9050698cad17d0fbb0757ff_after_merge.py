    def content_locate(self, account=None, reference=None, path=None, cid=None,
                       content=None, version=None, properties=True, **kwargs):
        """
        Get a description of the content along with the list of its chunks.

        :param cid: container id that can be used in place of `account`
            and `reference`
        :type cid: hexadecimal `str`
        :param content: content id that can be used in place of `path`
        :type content: hexadecimal `str`
        :param properties: should the request return object properties
            along with content description
        :type properties: `bool`
        :returns: a tuple with content metadata `dict` as first element
            and chunk `list` as second element
        """
        uri = self._make_uri('content/locate')
        params = self._make_params(account, reference, path, cid=cid,
                                   content=content, version=version)
        params['properties'] = properties
        try:
            resp, chunks = self._direct_request(
                'GET', uri, params=params, **kwargs)
            content_meta = extract_content_headers_meta(resp.headers)
        except exceptions.OioNetworkException as exc:
            # TODO(FVE): this special behavior can be removed when
            # the 'content/locate' protocol is changed to include
            # object properties in the response body instead of headers.
            if properties and 'got more than 100 headers' in str(exc):
                params['properties'] = False
                _resp, chunks = self._direct_request(
                    'GET', uri, params=params, **kwargs)
                content_meta = self.content_get_properties(
                    account, reference, path, cid=cid, content=content,
                    version=version, **kwargs)
            else:
                raise
        return content_meta, chunks