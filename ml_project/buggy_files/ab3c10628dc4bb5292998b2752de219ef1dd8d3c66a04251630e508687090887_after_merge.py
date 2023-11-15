def interpolate_text(template: Text, values: Dict[Text, Text]) -> Text:
    # transforming template tags from
    # "{tag_name}" to "{0[tag_name]}"
    # as described here:
    # https://stackoverflow.com/questions/7934620/python-dots-in-the-name-of-variable-in-a-format-string#comment9695339_7934969
    # black list character and make sure to not to allow
    # (a) newline in slot name
    # (b) { or } in slot name
    try:
        text = re.sub(r"{([^\n{}]+?)}", r"{0[\1]}", str(template))
        text = text.format(values)
        if "0[" in text:
            # regex replaced tag but format did not replace
            # likely cause would be that tag name was enclosed
            # in double curly and format func simply escaped it.
            # we don't want to return {0[SLOTNAME]} thus
            # restoring original value with { being escaped.
            return template.format({})

        return text
    except KeyError as e:
        logger.exception(
            "Failed to fill utterance template '{}'. "
            "Tried to replace '{}' but could not find "
            "a value for it. There is no slot with this "
            "name nor did you pass the value explicitly "
            "when calling the template. Return template "
            "without filling the template. "
            "".format(template, e.args[0])
        )
        return template