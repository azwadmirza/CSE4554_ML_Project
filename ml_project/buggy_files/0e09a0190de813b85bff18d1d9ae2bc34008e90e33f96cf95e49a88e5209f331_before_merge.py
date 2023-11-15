    def _check_conf_types(self, conf, conf_types):
        """Check that conf value is of the correct type."""
        for conf_key, conf_value in conf.items():
            test_config_condition(
                conf_key not in conf_types, '%s field unknown in %s (known types %s)' % (
                    conf_key, self._id, conf_types))
            if conf_value is not None:
                conf_type = conf_types[conf_key]
                test_config_condition(
                    not isinstance(conf_value, conf_type), '%s value %s must be %s not %s' % (
                        conf_key, conf_value,
                        conf_type, type(conf_value))) # pytype: disable=invalid-typevar