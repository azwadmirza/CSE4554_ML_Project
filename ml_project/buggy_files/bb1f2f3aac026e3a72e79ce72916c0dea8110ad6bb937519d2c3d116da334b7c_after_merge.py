    def _get_base_query(self, query=None, filters=None, order_column='', order_direction=''):
        if filters:
            query = filters.apply_all(query)
        if order_column != '':
            # if Model has custom decorator **renders('<COL_NAME>')**
            # this decorator will add a property to the method named *_col_name*
            if hasattr(self.obj, order_column):
                if hasattr(getattr(self.obj, order_column), '_col_name'):
                    order_column = getattr(self._get_attr(order_column), '_col_name')
            if order_direction == 'asc':
                query = query.order_by(self._get_attr(order_column).asc())
            else:
                query = query.order_by(self._get_attr(order_column).desc())
        return query