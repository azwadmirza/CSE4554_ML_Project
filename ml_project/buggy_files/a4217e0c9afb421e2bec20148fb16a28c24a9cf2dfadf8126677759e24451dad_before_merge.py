    def _get_ongoing_dict_key(self, result):
        if not isinstance(result, BaseResult):
            raise ValueError(
                'Any result using _get_ongoing_dict_key must subclass from '
                'BaseResult. Provided result is of type: %s' % type(result)
            )
        return ':'.join(
            str(el) for el in [result.transfer_type, result.src, result.dest])