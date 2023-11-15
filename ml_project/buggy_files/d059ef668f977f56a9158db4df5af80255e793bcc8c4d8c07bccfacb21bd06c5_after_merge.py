    def expand(
        self, pipeline
    ) -> Tuple[Dict[Text, Optional[_Dataset]], Optional[Dict[Text, Dict[
        Text, beam.pvalue.PCollection]]]]:
      dataset_keys_list = [
          dataset.dataset_key for dataset in self._analyze_data_list
      ]
      # TODO(b/37788560): Remove this restriction when a greater number of
      # stages can be handled efficiently.
      cache_entry_keys = (
          tft_beam.analysis_graph_builder.get_analysis_cache_entry_keys(
              self._preprocessing_fn, self._feature_spec_or_typespec,
              dataset_keys_list, self._force_tf_compat_v1))
      # We estimate the number of stages in the pipeline to be roughly:
      # analyzers * analysis_paths * 10.
      if (len(cache_entry_keys) * len(dataset_keys_list) * 10 >
          _MAX_ESTIMATED_STAGES_COUNT):
        absl.logging.warning(
            'Disabling cache because otherwise the number of stages might be '
            'too high ({} analyzers, {} analysis paths)'.format(
                len(cache_entry_keys), len(dataset_keys_list)))
        # Returning None as the input cache here disables both input and output
        # cache.
        return ({d.dataset_key: d for d in self._analyze_data_list}, None)

      if self._input_cache_dir is not None:
        absl.logging.info('Reading the following analysis cache entry keys: %s',
                          cache_entry_keys)
        input_cache = (
            pipeline
            | 'ReadCache' >> analyzer_cache.ReadAnalysisCacheFromFS(
                self._input_cache_dir,
                dataset_keys_list,
                source=self._cache_source,
                cache_entry_keys=cache_entry_keys))
      elif self._output_cache_dir is not None:
        input_cache = {}
      else:
        # Using None here to indicate that this pipeline will not read or write
        # cache.
        input_cache = None

      if input_cache is None:
        # Cache is disabled so we won't be filtering out any datasets, and will
        # always perform a flatten over all of them.
        filtered_analysis_dataset_keys = dataset_keys_list
      else:
        filtered_analysis_dataset_keys = (
            tft_beam.analysis_graph_builder.get_analysis_dataset_keys(
                self._preprocessing_fn, self._feature_spec_or_typespec,
                dataset_keys_list, input_cache, self._force_tf_compat_v1))

      new_analyze_data_dict = {}
      for dataset in self._analyze_data_list:
        if dataset.dataset_key in filtered_analysis_dataset_keys:
          new_analyze_data_dict[dataset.dataset_key] = dataset
        else:
          new_analyze_data_dict[dataset.dataset_key] = None

      return (new_analyze_data_dict, input_cache)