    def _visible_variables(cls, domain):
        """Generate variables in order they should be presented in in combos."""
        return chain(
            cls.AllTypes,
            filter_visible(chain(domain.class_vars,
                                 domain.metas,
                                 domain.attributes)))