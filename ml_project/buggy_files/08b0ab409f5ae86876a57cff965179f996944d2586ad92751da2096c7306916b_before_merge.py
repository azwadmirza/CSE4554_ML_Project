    def _get_items(self):
        from conda.core.linked_data import linked
        packages = linked(context.prefix_w_legacy_search)
        return [dist.quad[0] for dist in packages]