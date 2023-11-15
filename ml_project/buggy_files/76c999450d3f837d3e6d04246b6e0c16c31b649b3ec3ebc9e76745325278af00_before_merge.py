def invert_mapping(mapping: Mapping[str, int]) -> Mapping[int, str]:
    """
    Invert a mapping.

    :param mapping:
        The mapping, key -> value.

    :return:
        The inverse mapping, value -> key.
    """
    num_unique_values = len(set(mapping.values()))
    num_keys = len(mapping)
    if num_unique_values < num_keys:
        raise ValueError(f'Mapping is not bijective! Only {num_unique_values}/{num_keys} are unique.')
    return {
        value: key
        for key, value in mapping.items()
    }