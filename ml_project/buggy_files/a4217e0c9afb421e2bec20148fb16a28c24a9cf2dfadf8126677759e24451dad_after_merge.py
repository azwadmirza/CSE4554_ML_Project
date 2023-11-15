    def _get_ongoing_dict_key(self, result):
        if not isinstance(result, BaseResult):
            raise ValueError(
                'Any result using _get_ongoing_dict_key must subclass from '
                'BaseResult. Provided result is of type: %s' % type(result)
            )
        key_parts = []
        for result_property in [result.transfer_type, result.src, result.dest]:
            if result_property is not None:
                key_parts.append(ensure_text_type(result_property))
        return u':'.join(key_parts)