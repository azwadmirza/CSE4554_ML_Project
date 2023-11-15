def interpolate(
    template: Union[Dict[Text, Any], Text], values: Dict[Text, Text]
) -> Union[Dict[Text, Any], Text]:
    if isinstance(template, str):
        return interpolate_text(template, values)
    elif isinstance(template, dict):
        for k, v in template.items():
            if isinstance(v, dict):
                interpolate(v, values)
            elif isinstance(v, list):
                template[k] = [interpolate(i, values) for i in v]
            else:
                template[k] = interpolate_text(v, values)
        return template
    return template