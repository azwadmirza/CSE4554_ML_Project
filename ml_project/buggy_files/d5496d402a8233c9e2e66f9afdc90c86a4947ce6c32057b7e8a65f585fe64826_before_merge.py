    def _get_filters_from_where_node(self, where_node, check_only=False):
        # Check if this is a leaf node
        if isinstance(where_node, Lookup):
            field_attname = where_node.lhs.target.attname
            lookup = where_node.lookup_name
            value = where_node.rhs

            # Ignore pointer fields that show up in specific page type queries
            if field_attname.endswith('_ptr_id'):
                return

            # Process the filter
            return self._process_filter(field_attname, lookup, value, check_only=check_only)

        elif isinstance(where_node, SubqueryConstraint):
            raise FilterError('Could not apply filter on search results: Subqueries are not allowed.')

        elif isinstance(where_node, WhereNode):
            # Get child filters
            connector = where_node.connector
            child_filters = [self._get_filters_from_where_node(child) for child in where_node.children]

            if not check_only:
                child_filters = [child_filter for child_filter in child_filters if child_filter]
                return self._connect_filters(child_filters, connector, where_node.negated)

        else:
            raise FilterError('Could not apply filter on search results: Unknown where node: ' + str(type(where_node)))