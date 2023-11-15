    def get_feature_meta(column, preprocessing_parameters, backend):
        tokenizer = get_from_registry(
            preprocessing_parameters['tokenizer'],
            tokenizer_registry
        )()
        max_length = 0
        for timeseries in column:
            processed_line = tokenizer(timeseries)
            max_length = max(max_length, len(processed_line))
        max_length = min(
            preprocessing_parameters['timeseries_length_limit'],
            max_length
        )

        return {'max_timeseries_length': max_length}