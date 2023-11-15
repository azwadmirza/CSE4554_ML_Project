    def _query_select_options(self, query, select_columns=None):
        """
            Add select load options to query. The goal
            is to only SQL select what is requested

        :param query: SQLAlchemy Query obj
        :param select_columns: (list) of columns
        :return: SQLAlchemy Query obj
        """
        if select_columns:
            _load_options = list()
            for column in select_columns:
                if "." in column:
                    model_relation = self.get_related_model(column.split(".")[0])
                    if not self.is_model_already_joinded(query, model_relation):
                        query = query.join(model_relation)
                    _load_options.append(
                        Load(model_relation).load_only(column.split(".")[1])
                    )
                else:
                    # is a custom property method field?
                    if hasattr(getattr(self.obj, column), "fget"):
                        pass
                    # is not a relation and not a function?
                    elif not self.is_relation(column) and not hasattr(
                        getattr(self.obj, column), "__call__"
                    ):
                        _load_options.append(Load(self.obj).load_only(column))
                    else:
                        _load_options.append(Load(self.obj))
            query = query.options(*tuple(_load_options))
        return query