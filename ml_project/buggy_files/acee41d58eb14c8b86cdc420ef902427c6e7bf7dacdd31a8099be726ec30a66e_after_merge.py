    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation.

        Must return a tuple of two dicts. The first is merged into the page's context,
        the second will be put into the uptodate list of all generated tasks.

        For hierarchical taxonomies, node is the `hierarchy_utils.TreeNode` element
        corresponding to the classification.

        Context must contain `title`, which should be something like 'Posts about <classification>'.
        """
        raise NotImplementedError()