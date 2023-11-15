def is_adhoc_metric(metric: Metric) -> bool:
    return isinstance(metric, dict)