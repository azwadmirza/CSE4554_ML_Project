def typify(value, type_hint=None):
    """Take a primitive value, usually a string, and try to make a more relevant type out of it.
    An optional type_hint will try to coerce the value to that type.

    Args:
        value (Any): Usually a string, not a sequence
        type_hint (type or Tuple[type]):

    Examples:
        >>> typify('32')
        32
        >>> typify('32', float)
        32.0
        >>> typify('32.0')
        32.0
        >>> typify('32.0.0')
        '32.0.0'
        >>> [typify(x) for x in ('true', 'yes', 'on')]
        [True, True, True]
        >>> [typify(x) for x in ('no', 'FALSe', 'off')]
        [False, False, False]
        >>> [typify(x) for x in ('none', 'None', None)]
        [None, None, None]

    """
    # value must be a string, or there at least needs to be a type hint
    if isinstance(value, string_types):
        value = value.strip()
    elif type_hint is None:
        # can't do anything because value isn't a string and there's no type hint
        return value

    # now we either have a stripped string, a type hint, or both
    # use the hint if it exists
    if isiterable(type_hint):
        if isinstance(type_hint, type) and issubclass(type_hint, Enum):
            try:
                return type_hint(value)
            except ValueError as e:
                try:
                    return type_hint[value]
                except KeyError:
                    raise TypeCoercionError(value, text_type(e))
        type_hint = set(type_hint)
        if not (type_hint - NUMBER_TYPES_SET):
            return numberify(value)
        elif not (type_hint - STRING_TYPES_SET):
            return text_type(value)
        elif not (type_hint - {bool, NoneType}):
            return boolify(value, nullable=True)
        elif not (type_hint - (STRING_TYPES_SET | {bool})):
            return boolify(value, return_string=True)
        elif not (type_hint - (STRING_TYPES_SET | {NoneType})):
            value = text_type(value)
            return None if value.lower() == 'none' else value
        elif not (type_hint - {bool, int}):
            return typify_str_no_hint(text_type(value))
        else:
            raise NotImplementedError()
    elif type_hint is not None:
        # coerce using the type hint, or use boolify for bool
        try:
            return boolify(value) if type_hint == bool else type_hint(value)
        except ValueError as e:
            # ValueError: invalid literal for int() with base 10: 'nope'
            raise TypeCoercionError(value, text_type(e))
    else:
        # no type hint, but we know value is a string, so try to match with the regex patterns
        #   if there's still no match, `typify_str_no_hint` will return `value`
        return typify_str_no_hint(value)