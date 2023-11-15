    def content_locate(self, account=None, reference=None, path=None, cid=None,
                       content=None, version=None, **kwargs):
        """
        Get a description of the content along with the list of its chunks.

        :param cid: container id that can be used in place of `account`
            and `reference`
        :type cid: hexadecimal `str`
        :param content: content id that can be used in place of `path`
        :type content: hexadecimal `str`
        :returns: a tuple with content metadata `dict` as first element
            and chunk `list` as second element
        """
        uri = self._make_uri('content/locate')
        params = self._make_params(account, reference, path, cid=cid,
                                   content=content, version=version)
        resp, chunks = self._direct_request(
                'GET', uri, params=params, **kwargs)
        # FIXME(FVE): see extract_content_headers_meta() code
        content_meta = extract_content_headers_meta(resp.headers)
        return content_meta, chunks