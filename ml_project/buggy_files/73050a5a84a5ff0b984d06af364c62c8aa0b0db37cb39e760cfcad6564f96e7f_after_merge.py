def interpolate(
    template: Union[Dict[Text, Any], Text], values: Dict[Text, Text]
) -> Union[Dict[Text, Any], Text]:
    """Recursively process template and interpolate any text keys.

    Args:
        template: The template that should be interpolated.
        values: A dictionary of keys and the values that those
            keys should be replaced with.

    Returns:
        The template with any replacements made.
    """
    if isinstance(template, str):
        return interpolate_text(template, values)
    elif isinstance(template, dict):
        for k, v in template.items():
            if isinstance(v, dict):
                interpolate(v, values)
            elif isinstance(v, list):
                template[k] = [interpolate(i, values) for i in v]
            elif isinstance(v, str):
                template[k] = interpolate_text(v, values)
        return template
    return template