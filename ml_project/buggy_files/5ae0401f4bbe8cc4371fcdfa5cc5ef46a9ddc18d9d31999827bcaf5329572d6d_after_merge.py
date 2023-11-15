def process_deprecated_setting(config: Dict[str, Any],
                               section1: str, name1: str,
                               section2: str, name2: str) -> None:
    section2_config = config.get(section2, {})

    if name2 in section2_config:
        logger.warning(
            "DEPRECATED: "
            f"The `{section2}.{name2}` setting is deprecated and "
            "will be removed in the next versions of Freqtrade. "
            f"Please use the `{section1}.{name1}` setting in your configuration instead."
        )
        section1_config = config.get(section1, {})
        section1_config[name1] = section2_config[name2]