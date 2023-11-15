    def to_metric(self, desc, tag_values, agg_data):
        """ to_metric translate the data that OpenCensus create
        to Prometheus format, using Prometheus Metric object

        :type desc: dict
        :param desc: The map that describes view definition

        :type tag_values: tuple of :class:
            `~opencensus.tags.tag_value.TagValue`
        :param object of opencensus.tags.tag_value.TagValue:
            TagValue object used as label values

        :type agg_data: object of :class:
            `~opencensus.stats.aggregation_data.AggregationData`
        :param object of opencensus.stats.aggregation_data.AggregationData:
            Aggregated data that needs to be converted as Prometheus samples

        :rtype: :class:`~prometheus_client.core.CounterMetricFamily` or
                :class:`~prometheus_client.core.HistogramMetricFamily` or
                :class:`~prometheus_client.core.UntypedMetricFamily` or
                :class:`~prometheus_client.core.GaugeMetricFamily`
        :returns: A Prometheus metric object
        """
        metric_name = desc['name']
        metric_description = desc['documentation']
        label_keys = desc['labels']

        # Prometheus requires that all tag values be strings hence
        # the need to cast none to the empty string before exporting. See
        # https://github.com/census-instrumentation/opencensus-python/issues/480
        tag_values = [tv if tv else "" for tv in tag_values]

        if isinstance(agg_data, aggregation_data_module.CountAggregationData):
            metric = CounterMetricFamily(name=metric_name,
                                         documentation=metric_description,
                                         labels=label_keys)
            metric.add_metric(labels=tag_values,
                              value=agg_data.count_data)
            return metric

        elif isinstance(agg_data,
                        aggregation_data_module.DistributionAggregationData):

            assert(agg_data.bounds == sorted(agg_data.bounds))
            points = {}
            cum_count = 0
            for ii, bound in enumerate(agg_data.bounds):
                cum_count += agg_data.counts_per_bucket[ii]
                points[str(bound)] = cum_count
            metric = HistogramMetricFamily(name=metric_name,
                                           documentation=metric_description,
                                           labels=label_keys)
            metric.add_metric(labels=tag_values,
                              buckets=list(points.items()),
                              sum_value=agg_data.sum,)
            return metric

        elif isinstance(agg_data,
                        aggregation_data_module.SumAggregationDataFloat):
            metric = UntypedMetricFamily(name=metric_name,
                                         documentation=metric_description,
                                         labels=label_keys)
            metric.add_metric(labels=tag_values,
                              value=agg_data.sum_data)
            return metric

        elif isinstance(agg_data,
                        aggregation_data_module.LastValueAggregationData):
            metric = GaugeMetricFamily(name=metric_name,
                                       documentation=metric_description,
                                       labels=label_keys)
            metric.add_metric(labels=tag_values,
                              value=agg_data.value)
            return metric

        else:
            raise ValueError("unsupported aggregation type %s"
                             % type(agg_data))