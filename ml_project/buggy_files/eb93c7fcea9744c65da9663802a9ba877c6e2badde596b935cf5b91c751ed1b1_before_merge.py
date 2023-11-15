    def create_time_series_list(self, v_data, option_resource_type,
                                metric_prefix):
        """ Create the TimeSeries object based on the view data
        """
        time_series_list = []
        aggregation_type = v_data.view.aggregation.aggregation_type
        tag_agg = v_data.tag_value_aggregation_data_map
        for tag_value, agg in tag_agg.items():
            series = monitoring_v3.types.TimeSeries()
            series.metric.type = namespaced_view_name(v_data.view.name,
                                                      metric_prefix)
            set_metric_labels(series, v_data.view, tag_value)
            set_monitored_resource(series, option_resource_type)

            point = series.points.add()
            if aggregation_type is aggregation.Type.DISTRIBUTION:
                dist_value = point.value.distribution_value
                dist_value.count = agg.count_data
                dist_value.mean = agg.mean_data

                sum_of_sqd = agg.sum_of_sqd_deviations
                dist_value.sum_of_squared_deviation = sum_of_sqd

                # Uncomment this when stackdriver supports Range
                # point.value.distribution_value.range.min = agg_data.min
                # point.value.distribution_value.range.max = agg_data.max
                bounds = dist_value.bucket_options.explicit_buckets.bounds
                buckets = dist_value.bucket_counts

                # Stackdriver expects a first bucket for samples in (-inf, 0),
                # but we record positive samples only, and our first bucket is
                # [0, first_bound).
                bounds.extend([0])
                buckets.extend([0])
                bounds.extend(list(map(float, agg.bounds)))
                buckets.extend(list(map(int, agg.counts_per_bucket)))
            elif aggregation_type is aggregation.Type.COUNT:
                point.value.int64_value = agg.count_data
            elif aggregation_type is aggregation.Type.SUM:
                if isinstance(v_data.view.measure, measure.MeasureInt):
                    # TODO: Add implementation of sum aggregation that does not
                    # store it's data as a float.
                    point.value.int64_value = int(agg.sum_data)
                if isinstance(v_data.view.measure, measure.MeasureFloat):
                    point.value.double_value = float(agg.sum_data)
            elif aggregation_type is aggregation.Type.LASTVALUE:
                if isinstance(v_data.view.measure, measure.MeasureInt):
                    point.value.int64_value = int(agg.value)
                if isinstance(v_data.view.measure, measure.MeasureFloat):
                    point.value.double_value = float(agg.value)
            else:
                raise TypeError("Unsupported aggregation type: %s" %
                                type(v_data.view.aggregation))

            start = datetime.strptime(v_data.start_time, EPOCH_PATTERN)
            end = datetime.strptime(v_data.end_time, EPOCH_PATTERN)

            timestamp_start = (start - EPOCH_DATETIME).total_seconds()
            timestamp_end = (end - EPOCH_DATETIME).total_seconds()

            point.interval.end_time.seconds = int(timestamp_end)

            secs = point.interval.end_time.seconds
            point.interval.end_time.nanos = int((timestamp_end - secs) * 10**9)

            if aggregation_type is not aggregation.Type.LASTVALUE:
                if timestamp_start == timestamp_end:
                    # avoiding start_time and end_time to be equal
                    timestamp_start = timestamp_start - 1

            start_time = point.interval.start_time
            start_time.seconds = int(timestamp_start)
            start_secs = start_time.seconds
            start_time.nanos = int((timestamp_start - start_secs) * 1e9)

            time_series_list.append(series)

        return time_series_list