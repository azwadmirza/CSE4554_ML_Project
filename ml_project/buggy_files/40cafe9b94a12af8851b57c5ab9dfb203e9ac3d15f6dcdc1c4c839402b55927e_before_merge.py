    def perform_query(self, **kwargs):
        """
        Fetch results for a given query.
        """
        if 'first' not in kwargs or 'last' not in kwargs:
            kwargs["first"], kwargs[
                'last'] = self.model.rowCount() + 1, self.model.rowCount() + self.model.item_load_batch

        # Create a new uuid for each new search
        if kwargs['first'] == 1 or not self.query_uuid:
            self.query_uuid = uuid.uuid4().hex
        kwargs.update({"uuid": self.query_uuid})

        sort_by, sort_asc = self._get_sort_parameters()

        if sort_by is not None:
            kwargs.update({"sort_by": sort_by, "sort_asc": sort_asc})

        if 'query_filter' in kwargs:
            kwargs.update({"filter": to_fts_query(kwargs.pop('query_filter'))})
        elif self.query_text:
            kwargs.update({"filter": self.query_text})

        if self.model.hide_xxx is not None:
            kwargs.update({"hide_xxx": self.model.hide_xxx})

        rest_endpoint_url = kwargs.pop("rest_endpoint_url")
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request(rest_endpoint_url,
                                         self.on_query_results,
                                         url_params=kwargs)

        # If it is the first time we fetch the results, so we must get the total number of items as well
        if self.model.total_items is None:
            self.query_total_count(rest_endpoint_url=rest_endpoint_url, **kwargs)