def _deserialize_component_stats(serialized_component_stats):
    from pandera import Check  # pylint: disable=import-outside-toplevel

    pandas_dtype = PandasDtype.from_str_alias(
        serialized_component_stats["pandas_dtype"]
    )
    checks = None
    if serialized_component_stats["checks"] is not None:
        checks = [
            _deserialize_check_stats(
                getattr(Check, check_name), check_stats, pandas_dtype
            )
            for check_name, check_stats in serialized_component_stats[
                "checks"
            ].items()
        ]
    return {
        "pandas_dtype": pandas_dtype,
        "nullable": serialized_component_stats["nullable"],
        "checks": checks,
        **{
            key: serialized_component_stats.get(key)
            for key in [
                "name",
                "allow_duplicates",
                "coerce",
                "required",
                "regex",
            ]
            if key in serialized_component_stats
        },
    }