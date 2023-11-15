    def _parse_search_registered_models_order_by(cls, order_by_list):
        """Sorts a set of registered models based on their natural ordering and an overriding set
        of order_bys. Registered models are naturally ordered first by name ascending.
        """
        clauses = []
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
                if ascending:
                    clauses.append(field.asc())
                else:
                    clauses.append(field.desc())

        clauses.append(SqlRegisteredModel.name.asc())
        return clauses