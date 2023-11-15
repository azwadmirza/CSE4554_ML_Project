    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError as e:
            from .utils.log_deprecation import LOG_DEPRECATION_MSG, MODULES_WITH_LOG_PARAMS

            if any(isinstance(self, mod_type) for mod_type in MODULES_WITH_LOG_PARAMS) and "log_" in name:
                base_name = name.split("log_")[1]  # e.g. log_lengthscale -> lengthscale
                raw_name = "raw_" + base_name
                warnings.warn(LOG_DEPRECATION_MSG.format(log_name=name, name=raw_name), DeprecationWarning)
                return super().__getattribute__(base_name).log()  # Get real param value and transform to log
            else:
                try:
                    return super().__getattribute__(name)
                except AttributeError:
                    raise e