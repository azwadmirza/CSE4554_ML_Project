    def _apply_view_derivers(self, info):
        d = pyramid.viewderivers

        # These derivers are not really derivers and so have fixed order
        outer_derivers = [('attr_wrapped_view', d.attr_wrapped_view),
                          ('predicated_view', d.predicated_view)]

        view = info.original_view
        derivers = self.registry.getUtility(IViewDerivers)
        for name, deriver in reversed(outer_derivers + derivers.sorted()):
            view = wraps_view(deriver)(view, info)
        return view