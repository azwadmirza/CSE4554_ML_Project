    def postprocess_posts_per_classification(self, posts_per_classification_per_language, flat_hierarchy_per_lang=None, hierarchy_lookup_per_lang=None):
        """Rearrange, modify or otherwise use the list of posts per classification and per language.

        For compatibility reasons, the list could be stored somewhere else as well.

        In case `has_hierarchy` is `True`, `flat_hierarchy_per_lang` is the flat
        hierarchy consisting of `hierarchy_utils.TreeNode` elements, and
        `hierarchy_lookup_per_lang` is the corresponding hierarchy lookup mapping
        classification strings to `hierarchy_utils.TreeNode` objects.
        """
        pass