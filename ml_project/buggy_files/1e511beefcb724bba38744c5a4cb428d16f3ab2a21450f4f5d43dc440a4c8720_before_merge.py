def _get_data_points(
    sdk_metric: MetricRecord, data_point_class: Type[DataPointT]
) -> List[DataPointT]:

    data_points = []

    for (
        label,
        bound_counter,
    ) in sdk_metric.instrument.bound_instruments.items():

        string_key_values = []

        for label_key, label_value in label:
            string_key_values.append(
                StringKeyValue(key=label_key, value=label_value)
            )

        for view_data in bound_counter.view_datas:

            if view_data.labels == label:

                data_points.append(
                    data_point_class(
                        labels=string_key_values,
                        value=view_data.aggregator.current,
                        start_time_unix_nano=(
                            view_data.aggregator.last_checkpoint_timestamp
                        ),
                        time_unix_nano=(
                            view_data.aggregator.last_update_timestamp
                        ),
                    )
                )
                break

    return data_points