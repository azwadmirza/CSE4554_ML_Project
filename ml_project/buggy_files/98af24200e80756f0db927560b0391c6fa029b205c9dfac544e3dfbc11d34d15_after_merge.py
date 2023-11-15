    def get_sqla_query(  # sqla
        self,
        metrics,
        granularity,
        from_dttm,
        to_dttm,
        columns=None,
        groupby=None,
        filter=None,
        is_timeseries=True,
        timeseries_limit=15,
        timeseries_limit_metric=None,
        row_limit=None,
        inner_from_dttm=None,
        inner_to_dttm=None,
        orderby=None,
        extras=None,
        order_desc=True,
    ) -> SqlaQuery:
        """Querying any sqla table from this common interface"""
        template_kwargs = {
            "from_dttm": from_dttm,
            "groupby": groupby,
            "metrics": metrics,
            "row_limit": row_limit,
            "to_dttm": to_dttm,
            "filter": filter,
            "columns": {col.column_name: col for col in self.columns},
        }
        is_sip_38 = is_feature_enabled("SIP_38_VIZ_REARCHITECTURE")
        template_kwargs.update(self.template_params_dict)
        extra_cache_keys: List[Any] = []
        template_kwargs["extra_cache_keys"] = extra_cache_keys
        template_processor = self.get_template_processor(**template_kwargs)
        db_engine_spec = self.database.db_engine_spec
        prequeries: List[str] = []

        orderby = orderby or []

        # For backward compatibility
        if granularity not in self.dttm_cols:
            granularity = self.main_dttm_col

        # Database spec supports join-free timeslot grouping
        time_groupby_inline = db_engine_spec.time_groupby_inline

        cols: Dict[str, Column] = {col.column_name: col for col in self.columns}
        metrics_dict: Dict[str, SqlMetric] = {m.metric_name: m for m in self.metrics}

        if not granularity and is_timeseries:
            raise Exception(
                _(
                    "Datetime column not provided as part table configuration "
                    "and is required by this type of chart"
                )
            )
        if (
            not metrics
            and not columns
            and (is_sip_38 or (not is_sip_38 and not groupby))
        ):
            raise Exception(_("Empty query?"))
        metrics_exprs: List[ColumnElement] = []
        for m in metrics:
            if utils.is_adhoc_metric(m):
                metrics_exprs.append(self.adhoc_metric_to_sqla(m, cols))
            elif m in metrics_dict:
                metrics_exprs.append(metrics_dict[m].get_sqla_col())
            else:
                raise Exception(_("Metric '%(metric)s' does not exist", metric=m))
        if metrics_exprs:
            main_metric_expr = metrics_exprs[0]
        else:
            main_metric_expr, label = literal_column("COUNT(*)"), "ccount"
            main_metric_expr = self.make_sqla_column_compatible(main_metric_expr, label)

        select_exprs: List[Column] = []
        groupby_exprs_sans_timestamp: OrderedDict = OrderedDict()

        if (is_sip_38 and metrics and columns) or (not is_sip_38 and groupby):
            # dedup columns while preserving order
            groupby = list(dict.fromkeys(columns if is_sip_38 else groupby))

            select_exprs = []
            for s in groupby:
                if s in cols:
                    outer = cols[s].get_sqla_col()
                else:
                    outer = literal_column(f"({s})")
                    outer = self.make_sqla_column_compatible(outer, s)

                groupby_exprs_sans_timestamp[outer.name] = outer
                select_exprs.append(outer)
        elif columns:
            for s in columns:
                select_exprs.append(
                    cols[s].get_sqla_col()
                    if s in cols
                    else self.make_sqla_column_compatible(literal_column(s))
                )
            metrics_exprs = []

        time_range_endpoints = extras.get("time_range_endpoints")
        groupby_exprs_with_timestamp = OrderedDict(groupby_exprs_sans_timestamp.items())
        if granularity:
            dttm_col = cols[granularity]
            time_grain = extras.get("time_grain_sqla")
            time_filters = []

            if is_timeseries:
                timestamp = dttm_col.get_timestamp_expression(time_grain)
                select_exprs += [timestamp]
                groupby_exprs_with_timestamp[timestamp.name] = timestamp

            # Use main dttm column to support index with secondary dttm columns.
            if (
                db_engine_spec.time_secondary_columns
                and self.main_dttm_col in self.dttm_cols
                and self.main_dttm_col != dttm_col.column_name
            ):
                time_filters.append(
                    cols[self.main_dttm_col].get_time_filter(
                        from_dttm, to_dttm, time_range_endpoints
                    )
                )
            time_filters.append(
                dttm_col.get_time_filter(from_dttm, to_dttm, time_range_endpoints)
            )

        select_exprs += metrics_exprs

        labels_expected = [c._df_label_expected for c in select_exprs]

        select_exprs = db_engine_spec.make_select_compatible(
            groupby_exprs_with_timestamp.values(), select_exprs
        )
        qry = sa.select(select_exprs)

        tbl = self.get_from_clause(template_processor)

        if (is_sip_38 and metrics) or (not is_sip_38 and not columns):
            qry = qry.group_by(*groupby_exprs_with_timestamp.values())

        where_clause_and = []
        having_clause_and: List = []
        for flt in filter:
            if not all([flt.get(s) for s in ["col", "op"]]):
                continue
            col = flt["col"]
            op = flt["op"].upper()
            col_obj = cols.get(col)
            if col_obj:
                is_list_target = op in (
                    utils.FilterOperator.IN.value,
                    utils.FilterOperator.NOT_IN.value,
                )
                eq = self.filter_values_handler(
                    values=flt.get("val"),
                    target_column_is_numeric=col_obj.is_numeric,
                    is_list_target=is_list_target,
                )
                if op in (
                    utils.FilterOperator.IN.value,
                    utils.FilterOperator.NOT_IN.value,
                ):
                    cond = col_obj.get_sqla_col().in_(eq)
                    if isinstance(eq, str) and NULL_STRING in eq:
                        cond = or_(cond, col_obj.get_sqla_col() is None)
                    if op == utils.FilterOperator.NOT_IN.value:
                        cond = ~cond
                    where_clause_and.append(cond)
                else:
                    if col_obj.is_numeric:
                        eq = utils.cast_to_num(flt["val"])
                    if op == utils.FilterOperator.EQUALS.value:
                        where_clause_and.append(col_obj.get_sqla_col() == eq)
                    elif op == utils.FilterOperator.NOT_EQUALS.value:
                        where_clause_and.append(col_obj.get_sqla_col() != eq)
                    elif op == utils.FilterOperator.GREATER_THAN.value:
                        where_clause_and.append(col_obj.get_sqla_col() > eq)
                    elif op == utils.FilterOperator.LESS_THAN.value:
                        where_clause_and.append(col_obj.get_sqla_col() < eq)
                    elif op == utils.FilterOperator.GREATER_THAN_OR_EQUALS.value:
                        where_clause_and.append(col_obj.get_sqla_col() >= eq)
                    elif op == utils.FilterOperator.LESS_THAN_OR_EQUALS.value:
                        where_clause_and.append(col_obj.get_sqla_col() <= eq)
                    elif op == utils.FilterOperator.LIKE.value:
                        where_clause_and.append(col_obj.get_sqla_col().like(eq))
                    elif op == utils.FilterOperator.IS_NULL.value:
                        where_clause_and.append(col_obj.get_sqla_col() == None)
                    elif op == utils.FilterOperator.IS_NOT_NULL.value:
                        where_clause_and.append(col_obj.get_sqla_col() != None)
                    else:
                        raise Exception(
                            _("Invalid filter operation type: %(op)s", op=op)
                        )
        if config["ENABLE_ROW_LEVEL_SECURITY"]:
            where_clause_and += self._get_sqla_row_level_filters(template_processor)
        if extras:
            where = extras.get("where")
            if where:
                where = template_processor.process_template(where)
                where_clause_and += [sa.text("({})".format(where))]
            having = extras.get("having")
            if having:
                having = template_processor.process_template(having)
                having_clause_and += [sa.text("({})".format(having))]
        if granularity:
            qry = qry.where(and_(*(time_filters + where_clause_and)))
        else:
            qry = qry.where(and_(*where_clause_and))
        qry = qry.having(and_(*having_clause_and))

        if not orderby and ((is_sip_38 and metrics) or (not is_sip_38 and not columns)):
            orderby = [(main_metric_expr, not order_desc)]

        # To ensure correct handling of the ORDER BY labeling we need to reference the
        # metric instance if defined in the SELECT clause.
        metrics_exprs_by_label = {m._label: m for m in metrics_exprs}

        for col, ascending in orderby:
            direction = asc if ascending else desc
            if utils.is_adhoc_metric(col):
                col = self.adhoc_metric_to_sqla(col, cols)
            elif col in cols:
                col = cols[col].get_sqla_col()

            if isinstance(col, Label) and col._label in metrics_exprs_by_label:
                col = metrics_exprs_by_label[col._label]

            qry = qry.order_by(direction(col))

        if row_limit:
            qry = qry.limit(row_limit)

        if (
            is_timeseries
            and timeseries_limit
            and not time_groupby_inline
            and ((is_sip_38 and columns) or (not is_sip_38 and groupby))
        ):
            if self.database.db_engine_spec.allows_joins:
                # some sql dialects require for order by expressions
                # to also be in the select clause -- others, e.g. vertica,
                # require a unique inner alias
                inner_main_metric_expr = self.make_sqla_column_compatible(
                    main_metric_expr, "mme_inner__"
                )
                inner_groupby_exprs = []
                inner_select_exprs = []
                for gby_name, gby_obj in groupby_exprs_sans_timestamp.items():
                    inner = self.make_sqla_column_compatible(gby_obj, gby_name + "__")
                    inner_groupby_exprs.append(inner)
                    inner_select_exprs.append(inner)

                inner_select_exprs += [inner_main_metric_expr]
                subq = select(inner_select_exprs).select_from(tbl)
                inner_time_filter = dttm_col.get_time_filter(
                    inner_from_dttm or from_dttm,
                    inner_to_dttm or to_dttm,
                    time_range_endpoints,
                )
                subq = subq.where(and_(*(where_clause_and + [inner_time_filter])))
                subq = subq.group_by(*inner_groupby_exprs)

                ob = inner_main_metric_expr
                if timeseries_limit_metric:
                    ob = self._get_timeseries_orderby(
                        timeseries_limit_metric, metrics_dict, cols
                    )
                direction = desc if order_desc else asc
                subq = subq.order_by(direction(ob))
                subq = subq.limit(timeseries_limit)

                on_clause = []
                for gby_name, gby_obj in groupby_exprs_sans_timestamp.items():
                    # in this case the column name, not the alias, needs to be
                    # conditionally mutated, as it refers to the column alias in
                    # the inner query
                    col_name = db_engine_spec.make_label_compatible(gby_name + "__")
                    on_clause.append(gby_obj == column(col_name))

                tbl = tbl.join(subq.alias(), and_(*on_clause))
            else:
                if timeseries_limit_metric:
                    orderby = [
                        (
                            self._get_timeseries_orderby(
                                timeseries_limit_metric, metrics_dict, cols
                            ),
                            False,
                        )
                    ]

                # run prequery to get top groups
                prequery_obj = {
                    "is_timeseries": False,
                    "row_limit": timeseries_limit,
                    "metrics": metrics,
                    "granularity": granularity,
                    "from_dttm": inner_from_dttm or from_dttm,
                    "to_dttm": inner_to_dttm or to_dttm,
                    "filter": filter,
                    "orderby": orderby,
                    "extras": extras,
                    "columns": columns,
                    "order_desc": True,
                }
                if not is_sip_38:
                    prequery_obj["groupby"] = groupby

                result = self.query(prequery_obj)
                prequeries.append(result.query)
                dimensions = [
                    c
                    for c in result.df.columns
                    if c not in metrics and c in groupby_exprs_sans_timestamp
                ]
                top_groups = self._get_top_groups(
                    result.df, dimensions, groupby_exprs_sans_timestamp
                )
                qry = qry.where(top_groups)
        return SqlaQuery(
            extra_cache_keys=extra_cache_keys,
            labels_expected=labels_expected,
            sqla_query=qry.select_from(tbl),
            prequeries=prequeries,
        )