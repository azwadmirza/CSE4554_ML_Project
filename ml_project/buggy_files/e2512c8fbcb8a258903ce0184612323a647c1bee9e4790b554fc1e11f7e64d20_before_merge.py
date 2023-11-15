    def run_query(  # druid
        self,
        metrics: List[Metric],
        granularity: str,
        from_dttm: datetime,
        to_dttm: datetime,
        columns: Optional[List[str]] = None,
        groupby: Optional[List[str]] = None,
        filter: Optional[List[Dict[str, Any]]] = None,
        is_timeseries: Optional[bool] = True,
        timeseries_limit: Optional[int] = None,
        timeseries_limit_metric: Optional[Metric] = None,
        row_limit: Optional[int] = None,
        row_offset: Optional[int] = None,
        inner_from_dttm: Optional[datetime] = None,
        inner_to_dttm: Optional[datetime] = None,
        orderby: Optional[Any] = None,
        extras: Optional[Dict[str, Any]] = None,
        phase: int = 2,
        client: Optional["PyDruid"] = None,
        order_desc: bool = True,
    ) -> str:
        """Runs a query against Druid and returns a dataframe.
        """
        # TODO refactor into using a TBD Query object
        client = client or self.cluster.get_pydruid_client()
        row_limit = row_limit or conf.get("ROW_LIMIT")
        if row_offset:
            raise SupersetException("Offset not implemented for Druid connector")

        if not is_timeseries:
            granularity = "all"

        if granularity == "all":
            phase = 1
        inner_from_dttm = inner_from_dttm or from_dttm
        inner_to_dttm = inner_to_dttm or to_dttm

        timezone = from_dttm.replace(tzinfo=DRUID_TZ).tzname() if from_dttm else None

        query_str = ""
        metrics_dict = {m.metric_name: m for m in self.metrics}
        columns_dict = {c.column_name: c for c in self.columns}

        if self.cluster and LooseVersion(
            self.cluster.get_druid_version()
        ) < LooseVersion("0.11.0"):
            for metric in metrics:
                self.sanitize_metric_object(metric)
            if timeseries_limit_metric:
                self.sanitize_metric_object(timeseries_limit_metric)

        aggregations, post_aggs = DruidDatasource.metrics_and_post_aggs(
            metrics, metrics_dict
        )

        # the dimensions list with dimensionSpecs expanded
        columns_ = columns if IS_SIP_38 else groupby
        dimensions = self.get_dimensions(columns_, columns_dict) if columns_ else []

        extras = extras or {}
        qry = dict(
            datasource=self.datasource_name,
            dimensions=dimensions,
            aggregations=aggregations,
            granularity=DruidDatasource.granularity(
                granularity, timezone=timezone, origin=extras.get("druid_time_origin")
            ),
            post_aggregations=post_aggs,
            intervals=self.intervals_from_dttms(from_dttm, to_dttm),
        )

        if is_timeseries:
            qry["context"] = dict(skipEmptyBuckets=True)

        filters = (
            DruidDatasource.get_filters(filter, self.num_cols, columns_dict)
            if filter
            else None
        )
        if filters:
            qry["filter"] = filters

        if "having_druid" in extras:
            having_filters = self.get_having_filters(extras["having_druid"])
            if having_filters:
                qry["having"] = having_filters
        else:
            having_filters = None

        order_direction = "descending" if order_desc else "ascending"

        if (IS_SIP_38 and not metrics and columns and "__time" not in columns) or (
            not IS_SIP_38 and columns
        ):
            columns.append("__time")
            del qry["post_aggregations"]
            del qry["aggregations"]
            del qry["dimensions"]
            qry["columns"] = columns
            qry["metrics"] = []
            qry["granularity"] = "all"
            qry["limit"] = row_limit
            client.scan(**qry)
        elif (IS_SIP_38 and columns) or (
            not IS_SIP_38 and not groupby and not having_filters
        ):
            logger.info("Running timeseries query for no groupby values")
            del qry["dimensions"]
            client.timeseries(**qry)
        elif (
            not having_filters
            and order_desc
            and (
                (IS_SIP_38 and columns and len(columns) == 1)
                or (not IS_SIP_38 and groupby and len(groupby) == 1)
            )
        ):
            dim = list(qry["dimensions"])[0]
            logger.info("Running two-phase topn query for dimension [{}]".format(dim))
            pre_qry = deepcopy(qry)
            order_by: Optional[str] = None
            if timeseries_limit_metric:
                order_by = utils.get_metric_name(timeseries_limit_metric)
                aggs_dict, post_aggs_dict = DruidDatasource.metrics_and_post_aggs(
                    [timeseries_limit_metric], metrics_dict
                )
                if phase == 1:
                    pre_qry["aggregations"].update(aggs_dict)
                    pre_qry["post_aggregations"].update(post_aggs_dict)
                else:
                    pre_qry["aggregations"] = aggs_dict
                    pre_qry["post_aggregations"] = post_aggs_dict
            else:
                agg_keys = qry["aggregations"].keys()
                order_by = list(agg_keys)[0] if agg_keys else None

            # Limit on the number of timeseries, doing a two-phases query
            pre_qry["granularity"] = "all"
            pre_qry["threshold"] = min(row_limit, timeseries_limit or row_limit)
            pre_qry["metric"] = order_by
            pre_qry["dimension"] = self._dimensions_to_values(qry["dimensions"])[0]
            del pre_qry["dimensions"]

            client.topn(**pre_qry)
            logger.info("Phase 1 Complete")
            if phase == 2:
                query_str += "// Two phase query\n// Phase 1\n"
            query_str += json.dumps(
                client.query_builder.last_query.query_dict, indent=2
            )
            query_str += "\n"
            if phase == 1:
                return query_str
            query_str += "// Phase 2 (built based on phase one's results)\n"
            df = client.export_pandas()
            if df is None:
                df = pd.DataFrame()
            qry["filter"] = self._add_filter_from_pre_query_data(
                df, [pre_qry["dimension"]], filters
            )
            qry["threshold"] = timeseries_limit or 1000
            if row_limit and granularity == "all":
                qry["threshold"] = row_limit
            qry["dimension"] = dim
            del qry["dimensions"]
            qry["metric"] = list(qry["aggregations"].keys())[0]
            client.topn(**qry)
            logger.info("Phase 2 Complete")
        elif having_filters or ((IS_SIP_38 and columns) or (not IS_SIP_38 and groupby)):
            # If grouping on multiple fields or using a having filter
            # we have to force a groupby query
            logger.info("Running groupby query for dimensions [{}]".format(dimensions))
            if timeseries_limit and is_timeseries:
                logger.info("Running two-phase query for timeseries")

                pre_qry = deepcopy(qry)
                pre_qry_dims = self._dimensions_to_values(qry["dimensions"])

                # Can't use set on an array with dicts
                # Use set with non-dict items only
                non_dict_dims = list(
                    set([x for x in pre_qry_dims if not isinstance(x, dict)])
                )
                dict_dims = [x for x in pre_qry_dims if isinstance(x, dict)]
                pre_qry["dimensions"] = non_dict_dims + dict_dims  # type: ignore

                order_by = None
                if metrics:
                    order_by = utils.get_metric_name(metrics[0])
                else:
                    order_by = pre_qry_dims[0]  # type: ignore

                if timeseries_limit_metric:
                    order_by = utils.get_metric_name(timeseries_limit_metric)
                    aggs_dict, post_aggs_dict = DruidDatasource.metrics_and_post_aggs(
                        [timeseries_limit_metric], metrics_dict
                    )
                    if phase == 1:
                        pre_qry["aggregations"].update(aggs_dict)
                        pre_qry["post_aggregations"].update(post_aggs_dict)
                    else:
                        pre_qry["aggregations"] = aggs_dict
                        pre_qry["post_aggregations"] = post_aggs_dict

                # Limit on the number of timeseries, doing a two-phases query
                pre_qry["granularity"] = "all"
                pre_qry["limit_spec"] = {
                    "type": "default",
                    "limit": min(timeseries_limit, row_limit),
                    "intervals": self.intervals_from_dttms(
                        inner_from_dttm, inner_to_dttm
                    ),
                    "columns": [{"dimension": order_by, "direction": order_direction}],
                }
                client.groupby(**pre_qry)
                logger.info("Phase 1 Complete")
                query_str += "// Two phase query\n// Phase 1\n"
                query_str += json.dumps(
                    client.query_builder.last_query.query_dict, indent=2
                )
                query_str += "\n"
                if phase == 1:
                    return query_str
                query_str += "// Phase 2 (built based on phase one's results)\n"
                df = client.export_pandas()
                if df is None:
                    df = pd.DataFrame()
                qry["filter"] = self._add_filter_from_pre_query_data(
                    df, pre_qry["dimensions"], qry["filter"]
                )
                qry["limit_spec"] = None
            if row_limit:
                dimension_values = self._dimensions_to_values(dimensions)
                qry["limit_spec"] = {
                    "type": "default",
                    "limit": row_limit,
                    "columns": [
                        {
                            "dimension": (
                                utils.get_metric_name(metrics[0])
                                if metrics
                                else dimension_values[0]
                            ),
                            "direction": order_direction,
                        }
                    ],
                }
            client.groupby(**qry)
            logger.info("Query Complete")
        query_str += json.dumps(client.query_builder.last_query.query_dict, indent=2)
        return query_str