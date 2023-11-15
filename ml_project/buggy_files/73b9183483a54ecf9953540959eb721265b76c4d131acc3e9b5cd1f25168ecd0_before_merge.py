    def __init__(self, model, parent, factory, resource_defs,
                 service_model):
        self._model = model
        operation_name = self._model.request.operation
        self._parent = parent

        search_path = model.path
        self._handler = ResourceHandler(search_path, factory, resource_defs,
            service_model, model.resource, operation_name)