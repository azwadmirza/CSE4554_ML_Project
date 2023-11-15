    def query(self, q=None, **kw):
        """Query Open Library.

        Open Library always limits the result to 1000 items due to
        performance issues. Pass limit=False to fetch all matching
        results by making multiple requests to the server. Please note
        that an iterator is returned instead of list when limit=False is
        passed.::

            >>> ol.query({'type': '/type/type', 'limit': 2}) #doctest: +SKIP
            [{'key': '/type/property'}, {'key': '/type/type'}]

            >>> ol.query(type='/type/type', limit=2) #doctest: +SKIP
            [{'key': '/type/property'}, {'key': '/type/type'}]
        """
        q = dict(q or {})
        q.update(kw)
        q = marshal(q)
        def unlimited_query(q):
            q['limit'] = 1000
            q.setdefault('offset', 0)
            q.setdefault('sort', 'key')

            while True:
                result = self.query(q)
                for r in result:
                    yield r
                if len(result) < 1000:
                    break
                q['offset'] += len(result)

        if 'limit' in q and q['limit'] == False:
            return unlimited_query(q)
        else:
            q = json.dumps(q)
            response = self._request("/query.json?" + urllib.parse.urlencode(dict(query=q)))
            return unmarshal(json.loads(response.read()))