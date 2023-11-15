    def _parse_search_registered_models_order_by(cls, order_by_list):
        """Sorts a set of registered models based on their natural ordering and an overriding set
        of order_bys. Registered models are naturally ordered first by name ascending.
        """
        clauses = []
        observed_order_by_clauses = set()
        if order_by_list:
            for order_by_clause in order_by_list:
                (
                    attribute_token,
                    ascending,
                ) = SearchUtils.parse_order_by_for_search_registered_models(order_by_clause)
                if attribute_token == SqlRegisteredModel.name.key:
                    field = SqlRegisteredModel.name
                elif attribute_token in SearchUtils.VALID_TIMESTAMP_ORDER_BY_KEYS:
                    field = SqlRegisteredModel.last_updated_time
                else:
                    raise MlflowException(
                        "Invalid order by key '{}' specified.".format(attribute_token)
                        + "Valid keys are "
                        + "'{}'".format(SearchUtils.RECOMMENDED_ORDER_BY_KEYS_REGISTERED_MODELS),
                        error_code=INVALID_PARAMETER_VALUE,
                    )
                if field.key in observed_order_by_clauses:
                    raise MlflowException(
                        "`order_by` contains duplicate fields: {}".format(order_by_list)
                    )
                observed_order_by_clauses.add(field.key)
                if ascending:
                    clauses.append(field.asc())
                else:
                    clauses.append(field.desc())

        if SqlRegisteredModel.name.key not in observed_order_by_clauses:
            clauses.append(SqlRegisteredModel.name.asc())
        return clauses