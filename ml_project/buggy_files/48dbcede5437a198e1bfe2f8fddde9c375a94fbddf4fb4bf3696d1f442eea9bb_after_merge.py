    def _translate_data(
        self, data: Sequence[MetricRecord]
    ) -> ExportMetricsServiceRequest:
        # pylint: disable=too-many-locals,no-member
        # pylint: disable=attribute-defined-outside-init

        sdk_resource_instrumentation_library_metrics = {}

        # The criteria to decide how to translate data is based on this table
        # taken directly from OpenTelemetry Proto v0.5.0:

        # TODO: Update table after the decision on:
        # https://github.com/open-telemetry/opentelemetry-specification/issues/731.
        # By default, metrics recording using the OpenTelemetry API are exported as
        # (the table does not include MeasurementValueType to avoid extra rows):
        #
        #   Instrument         Type
        #   ----------------------------------------------
        #   Counter            Sum(aggregation_temporality=delta;is_monotonic=true)
        #   UpDownCounter      Sum(aggregation_temporality=delta;is_monotonic=false)
        #   ValueRecorder      TBD
        #   SumObserver        Sum(aggregation_temporality=cumulative;is_monotonic=true)
        #   UpDownSumObserver  Sum(aggregation_temporality=cumulative;is_monotonic=false)
        #   ValueObserver      Gauge()
        for sdk_metric_record in data:

            if sdk_metric_record.resource not in (
                sdk_resource_instrumentation_library_metrics.keys()
            ):
                sdk_resource_instrumentation_library_metrics[
                    sdk_metric_record.resource
                ] = InstrumentationLibraryMetrics()

            type_class = {
                int: {
                    "sum": {"class": IntSum, "argument": "int_sum"},
                    "gauge": {"class": IntGauge, "argument": "int_gauge"},
                    "data_point_class": IntDataPoint,
                },
                float: {
                    "sum": {"class": DoubleSum, "argument": "double_sum"},
                    "gauge": {
                        "class": DoubleGauge,
                        "argument": "double_gauge",
                    },
                    "data_point_class": DoubleDataPoint,
                },
            }

            value_type = sdk_metric_record.instrument.value_type

            sum_class = type_class[value_type]["sum"]["class"]
            gauge_class = type_class[value_type]["gauge"]["class"]
            data_point_class = type_class[value_type]["data_point_class"]

            if isinstance(sdk_metric_record.instrument, Counter):
                otlp_metric_data = sum_class(
                    data_points=_get_data_points(
                        sdk_metric_record, data_point_class
                    ),
                    aggregation_temporality=(
                        AggregationTemporality.AGGREGATION_TEMPORALITY_DELTA
                    ),
                    is_monotonic=True,
                )
                argument = type_class[value_type]["sum"]["argument"]

            elif isinstance(sdk_metric_record.instrument, UpDownCounter):
                otlp_metric_data = sum_class(
                    data_points=_get_data_points(
                        sdk_metric_record, data_point_class
                    ),
                    aggregation_temporality=(
                        AggregationTemporality.AGGREGATION_TEMPORALITY_DELTA
                    ),
                    is_monotonic=False,
                )
                argument = type_class[value_type]["sum"]["argument"]

            elif isinstance(sdk_metric_record.instrument, (ValueRecorder)):
                logger.warning("Skipping exporting of ValueRecorder metric")
                continue

            elif isinstance(sdk_metric_record.instrument, SumObserver):
                otlp_metric_data = sum_class(
                    data_points=_get_data_points(
                        sdk_metric_record, data_point_class
                    ),
                    aggregation_temporality=(
                        AggregationTemporality.AGGREGATION_TEMPORALITY_CUMULATIVE
                    ),
                    is_monotonic=True,
                )
                argument = type_class[value_type]["sum"]["argument"]

            elif isinstance(sdk_metric_record.instrument, UpDownSumObserver):
                otlp_metric_data = sum_class(
                    data_points=_get_data_points(
                        sdk_metric_record, data_point_class
                    ),
                    aggregation_temporality=(
                        AggregationTemporality.AGGREGATION_TEMPORALITY_CUMULATIVE
                    ),
                    is_monotonic=False,
                )
                argument = type_class[value_type]["sum"]["argument"]

            elif isinstance(sdk_metric_record.instrument, (ValueObserver)):
                otlp_metric_data = gauge_class(
                    data_points=_get_data_points(
                        sdk_metric_record, data_point_class
                    )
                )
                argument = type_class[value_type]["gauge"]["argument"]

            sdk_resource_instrumentation_library_metrics[
                sdk_metric_record.resource
            ].metrics.append(
                OTLPMetric(
                    **{
                        "name": sdk_metric_record.instrument.name,
                        "description": (
                            sdk_metric_record.instrument.description
                        ),
                        "unit": sdk_metric_record.instrument.unit,
                        argument: otlp_metric_data,
                    }
                )
            )

        return ExportMetricsServiceRequest(
            resource_metrics=_get_resource_data(
                sdk_resource_instrumentation_library_metrics,
                ResourceMetrics,
                "metrics",
            )
        )