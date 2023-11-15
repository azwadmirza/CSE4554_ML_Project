def _extract_tags(attr):
    if attr is None:
        return None
    tags = []
    for attribute_key, attribute_value in attr.items():
        tag = _convert_attribute_to_tag(attribute_key, attribute_value)
        if tag is None:
            continue
        tags.append(tag)
    return tags