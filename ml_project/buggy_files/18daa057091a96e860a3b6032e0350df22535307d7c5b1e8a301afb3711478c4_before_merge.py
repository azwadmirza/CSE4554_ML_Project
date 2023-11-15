    def validate_cache_behavior(self, config, cache_behavior, valid_origins, is_default_cache=False):
        if is_default_cache and cache_behavior is None:
            cache_behavior = {}
        if cache_behavior is None and valid_origins is not None:
            return config
        cache_behavior = self.validate_cache_behavior_first_level_keys(config, cache_behavior, valid_origins, is_default_cache)
        cache_behavior = self.validate_forwarded_values(config, cache_behavior.get('forwarded_values'), cache_behavior)
        cache_behavior = self.validate_allowed_methods(config, cache_behavior.get('allowed_methods'), cache_behavior)
        cache_behavior = self.validate_lambda_function_associations(config, cache_behavior.get('lambda_function_associations'), cache_behavior)
        cache_behavior = self.validate_trusted_signers(config, cache_behavior.get('trusted_signers'), cache_behavior)
        return cache_behavior