def is_adhoc_metric(metric: Metric) -> bool:
    if not isinstance(metric, dict):
        return False
    metric = cast(Dict[str, Any], metric)
    return bool(
        (
            (
                metric.get("expressionType") == AdhocMetricExpressionType.SIMPLE
                and metric.get("column")
                and cast(Dict[str, Any], metric["column"]).get("column_name")
                and metric.get("aggregate")
            )
            or (
                metric.get("expressionType") == AdhocMetricExpressionType.SQL
                and metric.get("sqlExpression")
            )
        )
        and metric.get("label")
    )