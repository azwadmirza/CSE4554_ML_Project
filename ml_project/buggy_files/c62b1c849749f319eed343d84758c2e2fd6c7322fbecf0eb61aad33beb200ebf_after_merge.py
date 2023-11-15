    def _format_conditions(self, filters, id_field, modified_field,
                           prefix='filters'):
        """Format the filters list in SQL, with placeholders for safe escaping.

        .. note::
            All conditions are combined using AND.

        .. note::

            Field name and value are escaped as they come from HTTP API.

        :returns: A SQL string with placeholders, and a dict mapping
            placeholders to actual values.
        :rtype: tuple
        """
        operators = {
            COMPARISON.EQ: '=',
            COMPARISON.NOT: '<>',
            COMPARISON.IN: 'IN',
            COMPARISON.EXCLUDE: 'NOT IN',
        }

        conditions = []
        holders = {}
        for i, filtr in enumerate(filters):
            value = filtr.value

            if filtr.field == id_field:
                sql_field = 'id'
            elif filtr.field == modified_field:
                sql_field = 'as_epoch(last_modified)'
            else:
                # Safely escape field name
                field_holder = '%s_field_%s' % (prefix, i)
                holders[field_holder] = filtr.field

                # JSON operator ->> retrieves values as text.
                # If field is missing, we default to ''.
                sql_field = "coalesce(data->>:%s, '')" % field_holder
                if isinstance(value, (int, float)) and \
                   value not in (True, False):
                    sql_field = "(data->>:%s)::numeric" % field_holder

            if filtr.operator not in (COMPARISON.IN, COMPARISON.EXCLUDE):
                # For the IN operator, let psycopg escape the values list.
                # Otherwise JSON-ify the native value (e.g. True -> 'true')
                if not isinstance(filtr.value, six.string_types):
                    value = json.dumps(filtr.value).strip('"')
            else:
                value = tuple(value)
                if filtr.field == id_field:
                    value = tuple([v if isinstance(v, six.string_types)
                                   else None for v in value])
                if filtr.field == modified_field:
                    value = tuple([v if isinstance(v, six.integer_types)
                                   else None for v in value])

            # Safely escape value
            value_holder = '%s_value_%s' % (prefix, i)
            holders[value_holder] = value

            sql_operator = operators.setdefault(filtr.operator,
                                                filtr.operator.value)
            cond = "%s %s :%s" % (sql_field, sql_operator, value_holder)
            conditions.append(cond)

        safe_sql = ' AND '.join(conditions)
        return safe_sql, holders