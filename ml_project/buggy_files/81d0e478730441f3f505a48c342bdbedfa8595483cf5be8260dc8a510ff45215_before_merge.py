    def _build_components(**kwargs):
        def _make(field_name, value):
            if field_name not in IndexRecord.__fields__:
                raise CondaValueError('Cannot match on field %s' % (field_name,))
            elif isinstance(value, string_types):
                value = text_type(value)

            if hasattr(value, 'match'):
                matcher = value
            elif field_name in _implementors:
                matcher = _implementors[field_name](value)
            elif text_type(value):
                matcher = StrMatch(value)
            else:
                raise NotImplementedError()

            return field_name, matcher

        return frozendict(_make(key, value) for key, value in iteritems(kwargs))