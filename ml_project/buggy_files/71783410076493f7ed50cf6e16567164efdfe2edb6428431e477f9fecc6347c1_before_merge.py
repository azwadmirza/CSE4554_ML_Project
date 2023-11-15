    def run_validation(self, value):

        if not isinstance(value, list):
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

        if len(value) == 0:
            return

        # TODO: Remove in 1.0
        config_types = set(type(l) for l in value)

        if config_types.issubset(set([str, dict, ])):
            return value

        if config_types.issubset(set([str, list, ])):
            return legacy.pages_compat_shim(value)

        raise ValidationError("Invalid pages config.")