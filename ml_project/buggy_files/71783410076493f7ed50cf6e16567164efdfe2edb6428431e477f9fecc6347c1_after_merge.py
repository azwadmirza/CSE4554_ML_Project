    def run_validation(self, value):

        if not isinstance(value, list):
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

        if len(value) == 0:
            return

        # TODO: Remove in 1.0
        config_types = set(type(l) for l in value)

        if config_types.issubset(set([six.text_type, dict, ])):
            return value

        if config_types.issubset(set([six.text_type, list, ])):
            return legacy.pages_compat_shim(value)

        raise ValidationError("Invalid pages config. {0} {1}".format(
            config_types,
            set([six.text_type, dict, ])
        ))