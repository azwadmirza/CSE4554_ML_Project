    def _get_model(self, doc, root=None, parent=None, comm=None):
        if 'panel.models.vega' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('VegaPlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'vega\')\n')
            from ..models.vega import VegaPlot
        else:
            VegaPlot = getattr(sys.modules['panel.models.vega'], 'VegaPlot')

        sources = {}
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, sources)
        props = self._process_param_change(self._init_properties())
        self._get_dimensions(json, props)
        model = VegaPlot(data=json, data_sources=sources, **props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model