    def render_GET(self, request):
        """
        .. http:get:: /search/completions?q=(string:query)

        A GET request to this endpoint will return autocompletion suggestions for the given query. For instance,
        when searching for "pioneer", this endpoint might return "pioneer one" if that torrent is present in the
        local database. This endpoint can be used to suggest terms to users while they type their search query.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/search/completions?q=pioneer

            **Example response**:

            .. sourcecode:: javascript

                {
                    "completions": ["pioneer one", "pioneer movie"]
                }
        """
        if 'q' not in request.args:
            request.setResponseCode(http.BAD_REQUEST)
            return json.twisted_dumps({"error": "query parameter missing"})

        keywords = ensure_unicode(request.args[b'q'][0], 'utf-8').lower()
        # TODO: add XXX filtering for completion terms
        results = self.session.lm.mds.TorrentMetadata.get_auto_complete_terms(keywords, max_terms=5)
        return json.twisted_dumps({"completions": results})