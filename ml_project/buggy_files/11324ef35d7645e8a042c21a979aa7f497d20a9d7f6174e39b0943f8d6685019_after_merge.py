    def query(
        self,
        filters=None,
        order_column="",
        order_direction="",
        page=None,
        page_size=None,
        select_columns=None,
    ):
        """
            QUERY
            :param filters:
                dict with filters {<col_name>:<value,...}
            :param order_column:
                name of the column to order
            :param order_direction:
                the direction to order <'asc'|'desc'>
            :param page:
                the current page
            :param page_size:
                the current page size

        """
        query = self.session.query(self.obj)
        query, relation_tuple = self._query_join_dotted_column(query, order_column)
        query = self._query_select_options(query, select_columns)
        query_count = self.session.query(func.count('*')).select_from(self.obj)

        query_count = self._get_base_query(query=query_count, filters=filters)
        query = self._get_base_query(
            query=query,
            filters=filters,
            order_column=order_column,
            order_direction=order_direction,
        )

        count = query_count.scalar()

        if page:
            query = query.offset(page * page_size)
        if page_size:
            query = query.limit(page_size)
        return count, query.all()