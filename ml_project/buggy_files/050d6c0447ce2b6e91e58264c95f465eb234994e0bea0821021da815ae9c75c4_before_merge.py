    def category_path_to_category_name(self, category_path):
        """Translate a category path to a category name."""
        if self.config['CATEGORY_ALLOW_HIERARCHIES']:
            return utils.join_hierarchical_category_path(category_path)
        else:
            return ''.join(category_path)