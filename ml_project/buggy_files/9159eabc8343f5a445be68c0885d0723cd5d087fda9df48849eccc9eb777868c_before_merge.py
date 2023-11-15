    def parse_category_name(self, category_name):
        """Parse a category name into a hierarchy."""
        if self.config['CATEGORY_ALLOW_HIERARCHIES']:
            try:
                return utils.parse_escaped_hierarchical_category_name(category_name)
            except Exception as e:
                utils.LOGGER.error(str(e))
                sys.exit(1)
        else:
            return [category_name] if len(category_name) > 0 else []