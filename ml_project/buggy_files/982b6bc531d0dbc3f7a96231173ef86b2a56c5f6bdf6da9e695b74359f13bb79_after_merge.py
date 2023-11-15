    def update_model_definition_with_metadata(
            input_feature,
            feature_metadata,
            *args,
            **kwargs
    ):
        for dim in ['height', 'width', 'num_channels']:
            input_feature[dim] = feature_metadata['preprocessing'][dim]