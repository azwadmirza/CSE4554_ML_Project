    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._widget_type(**self._process_param_change(self._init_properties()))
        if root is None:
            root = model
        # Link parameters and bokeh model
        values = dict(self.get_param_values())
        properties = self._filter_properties(list(self._process_param_change(values)))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model