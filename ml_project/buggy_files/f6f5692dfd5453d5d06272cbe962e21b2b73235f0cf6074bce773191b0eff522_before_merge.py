def check_conflicting_settings(config: Dict[str, Any],
                               section1: str, name1: str,
                               section2: str, name2: str):
    section1_config = config.get(section1, {})
    section2_config = config.get(section2, {})
    if name1 in section1_config and name2 in section2_config:
        raise OperationalException(
            f"Conflicting settings `{section1}.{name1}` and `{section2}.{name2}` "
            "(DEPRECATED) detected in the configuration file. "
            "This deprecated setting will be removed in the next versions of Freqtrade. "
            f"Please delete it from your configuration and use the `{section1}.{name1}` "
            "setting instead."
        )