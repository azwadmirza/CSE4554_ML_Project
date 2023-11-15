    def import_ocaid(self, ocaid, require_marc=True):
        data = {'identifier': ocaid, 'require_marc': 'true' if require_marc else 'false'}
        return self._request('/api/import/ia', method='POST', data=urllib.parse.urlencode(data)).read()