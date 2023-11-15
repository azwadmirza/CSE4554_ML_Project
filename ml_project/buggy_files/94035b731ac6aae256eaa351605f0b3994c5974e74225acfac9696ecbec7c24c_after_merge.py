    def _override_attribute_helper(strategy, config: Dict[str, Any],
                                   attribute: str, default: Any):
        """
        Override attributes in the strategy.
        Prevalence:
        - Configuration
        - Strategy
        - default (if not None)
        """
        if attribute in config:
            setattr(strategy, attribute, config[attribute])
            logger.info("Override strategy '%s' with value in config file: %s.",
                        attribute, config[attribute])
        elif hasattr(strategy, attribute):
            val = getattr(strategy, attribute)
            # None's cannot exist in the config, so do not copy them
            if val is not None:
                config[attribute] = val
        # Explicitly check for None here as other "falsy" values are possible
        elif default is not None:
            setattr(strategy, attribute, default)
            config[attribute] = default