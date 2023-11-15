def interpolate_text(template, values):
    if isinstance(template, str):
        # transforming template tags from
        # "{tag_name}" to "{0[tag_name]}"
        # as described here:
        # https://stackoverflow.com/questions/7934620/python-dots-in-the-name-of-variable-in-a-format-string#comment9695339_7934969
        # assuming that slot_name do not contain newline character here
        try:
            text = re.sub(r"{([^\n]+?)}", r"{0[\1]}", template)
            return text.format(values)
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
    return template