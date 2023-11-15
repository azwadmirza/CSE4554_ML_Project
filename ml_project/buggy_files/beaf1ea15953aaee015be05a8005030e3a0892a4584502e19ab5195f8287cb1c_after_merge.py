    def _make_query_to_client(self, *query):
        """
        Given a query, look up the client and perform the query.

        Parameters
        ----------
        query : collection of `~sunpy.net.vso.attr` objects

        Returns
        -------
        response : `~sunpy.net.dataretriever.client.QueryResponse`

        client : `object`
		Instance of client class
        """
        candidate_widget_types = self._check_registered_widgets(*query)
        tmpclient = candidate_widget_types[0]()
        return tmpclient.query(*query), tmpclient