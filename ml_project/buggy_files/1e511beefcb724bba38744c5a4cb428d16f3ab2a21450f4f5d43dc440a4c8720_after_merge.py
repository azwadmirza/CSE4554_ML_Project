def _get_data_points(
    sdk_metric_record: MetricRecord, data_point_class: Type[DataPointT]
) -> List[DataPointT]:

    if isinstance(sdk_metric_record.aggregator, SumAggregator):
        value = sdk_metric_record.aggregator.checkpoint

    elif isinstance(sdk_metric_record.aggregator, MinMaxSumCountAggregator):
        # FIXME: How are values to be interpreted from this aggregator?
        raise Exception("MinMaxSumCount aggregator data not supported")

    elif isinstance(sdk_metric_record.aggregator, HistogramAggregator):
        # FIXME: How are values to be interpreted from this aggregator?
        raise Exception("Histogram aggregator data not supported")

    elif isinstance(sdk_metric_record.aggregator, LastValueAggregator):
        value = sdk_metric_record.aggregator.checkpoint

    elif isinstance(sdk_metric_record.aggregator, ValueObserverAggregator):
        value = sdk_metric_record.aggregator.checkpoint.last

    return [
        data_point_class(
            labels=[
                StringKeyValue(key=str(label_key), value=str(label_value))
                for label_key, label_value in sdk_metric_record.labels
            ],
            value=value,
            start_time_unix_nano=(
                sdk_metric_record.aggregator.initial_checkpoint_timestamp
            ),
            time_unix_nano=(
                sdk_metric_record.aggregator.last_update_timestamp
            ),
        )
    ]