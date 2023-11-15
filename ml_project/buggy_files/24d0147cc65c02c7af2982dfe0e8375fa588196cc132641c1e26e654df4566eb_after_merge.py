    def __init__(self, data_source, conditionals, ds=None,
                 field_parameters=None, base_object=None):
        validate_object(data_source, YTSelectionContainer)
        validate_iterable(conditionals)
        for condition in conditionals:
            validate_object(condition, string_types)
        validate_object(ds, Dataset)
        validate_object(field_parameters, dict)
        validate_object(base_object, YTSelectionContainer)
        if base_object is not None:
            # passing base_object explicitly has been deprecated,
            # but we handle it here for backward compatibility
            if data_source is not None:
                raise RuntimeError(
                    "Cannot use both base_object and data_source")
            data_source=base_object
        super(YTCutRegion, self).__init__(
            data_source.center, ds, field_parameters, data_source=data_source)
        self.conditionals = ensure_list(conditionals)
        self.base_object = data_source
        self._selector = None