    def _visible_variables(domain):
        """Generate variables in order they should be presented in in combos."""
        return filter_visible(chain(domain.class_vars,
                                    domain.metas,
                                    domain.attributes))