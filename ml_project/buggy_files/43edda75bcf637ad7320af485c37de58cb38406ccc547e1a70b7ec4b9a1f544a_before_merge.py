def _serialize_component_stats(component_stats):
    """
    Serialize column or index statistics into json/yaml-compatible format.
    """
    serialized_checks = None
    if component_stats["checks"] is not None:
        serialized_checks = {
            check_name: _serialize_check_stats(
                check_stats, component_stats["pandas_dtype"]
            )
            for check_name, check_stats in component_stats["checks"].items()
        }
    return {
        "pandas_dtype": component_stats["pandas_dtype"].value,
        "nullable": component_stats["nullable"],
        "checks": serialized_checks,
        **{
            key: component_stats.get(key) for key in
            ["name", "allow_duplicates", "coerce", "required", "regex"]
            if key in component_stats
        }
    }