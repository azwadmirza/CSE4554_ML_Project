    def get_filters(cls, raw_filters, num_cols, columns_dict) -> "Filter":
        """Given Superset filter data structure, returns pydruid Filter(s)"""
        filters = None
        for flt in raw_filters:
            col = flt.get("col")
            op = flt.get("op")
            eq = flt.get("val")
            if (
                not col
                or not op
                or (eq is None and op not in ("IS NULL", "IS NOT NULL"))
            ):
                continue

            # Check if this dimension uses an extraction function
            # If so, create the appropriate pydruid extraction object
            column_def = columns_dict.get(col)
            dim_spec = column_def.dimension_spec if column_def else None
            extraction_fn = None
            if dim_spec and "extractionFn" in dim_spec:
                (col, extraction_fn) = DruidDatasource._create_extraction_fn(dim_spec)

            cond = None
            is_numeric_col = col in num_cols
            is_list_target = op in ("in", "not in")
            eq = cls.filter_values_handler(
                eq,
                is_list_target=is_list_target,
                target_column_is_numeric=is_numeric_col,
            )

            # For these two ops, could have used Dimension,
            # but it doesn't support extraction functions
            if op == "==":
                cond = Filter(
                    dimension=col, value=eq, extraction_function=extraction_fn
                )
            elif op == "!=":
                cond = ~Filter(
                    dimension=col, value=eq, extraction_function=extraction_fn
                )
            elif op in ("in", "not in"):
                fields = []
                # ignore the filter if it has no value
                if not len(eq):
                    continue
                # if it uses an extraction fn, use the "in" operator
                # as Dimension isn't supported
                elif extraction_fn is not None:
                    cond = Filter(
                        dimension=col,
                        values=eq,
                        type="in",
                        extraction_function=extraction_fn,
                    )
                elif len(eq) == 1:
                    cond = Dimension(col) == eq[0]
                else:
                    for s in eq:
                        fields.append(Dimension(col) == s)
                    cond = Filter(type="or", fields=fields)
                if op == "not in":
                    cond = ~cond
            elif op == "regex":
                cond = Filter(
                    extraction_function=extraction_fn,
                    type="regex",
                    pattern=eq,
                    dimension=col,
                )

            # For the ops below, could have used pydruid's Bound,
            # but it doesn't support extraction functions
            elif op == ">=":
                cond = Filter(
                    type="bound",
                    extraction_function=extraction_fn,
                    dimension=col,
                    lowerStrict=False,
                    upperStrict=False,
                    lower=eq,
                    upper=None,
                    alphaNumeric=is_numeric_col,
                )
            elif op == "<=":
                cond = Filter(
                    type="bound",
                    extraction_function=extraction_fn,
                    dimension=col,
                    lowerStrict=False,
                    upperStrict=False,
                    lower=None,
                    upper=eq,
                    alphaNumeric=is_numeric_col,
                )
            elif op == ">":
                cond = Filter(
                    type="bound",
                    extraction_function=extraction_fn,
                    lowerStrict=True,
                    upperStrict=False,
                    dimension=col,
                    lower=eq,
                    upper=None,
                    alphaNumeric=is_numeric_col,
                )
            elif op == "<":
                cond = Filter(
                    type="bound",
                    extraction_function=extraction_fn,
                    upperStrict=True,
                    lowerStrict=False,
                    dimension=col,
                    lower=None,
                    upper=eq,
                    alphaNumeric=is_numeric_col,
                )
            elif op == "IS NULL":
                cond = Filter(dimension=col, value="")
            elif op == "IS NOT NULL":
                cond = ~Filter(dimension=col, value="")

            if filters:
                filters = Filter(type="and", fields=[cond, filters])
            else:
                filters = cond

        return filters