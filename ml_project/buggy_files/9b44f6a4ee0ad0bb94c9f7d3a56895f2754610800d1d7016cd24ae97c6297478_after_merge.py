  def Transform(self, inputs: Mapping[Text, Any], outputs: Mapping[Text, Any],
                status_file: Text) -> None:
    """Executes on request.

    This is the implementation part of transform executor. This is intended for
    using or extending the executor without artifact dependency.

    Args:
      inputs: A dictionary of labelled input values, including:
        - labels.COMPUTE_STATISTICS_LABEL: Whether compute statistics.
        - labels.SCHEMA_PATH_LABEL: Path to schema file.
        - labels.EXAMPLES_DATA_FORMAT_LABEL: Example data format, one of the
            enums from example_gen_pb2.PayloadFormat.
        - labels.ANALYZE_DATA_PATHS_LABEL: Paths or path patterns to analyze
          data.
        - labels.ANALYZE_PATHS_FILE_FORMATS_LABEL: File formats of paths to
          analyze data.
        - labels.TRANSFORM_DATA_PATHS_LABEL: Paths or path patterns to transform
          data.
        - labels.TRANSFORM_PATHS_FILE_FORMATS_LABEL: File formats of paths to
          transform data.
        - labels.MODULE_FILE: Path to a Python module that contains the
          preprocessing_fn, optional.
        - labels.PREPROCESSING_FN: Path to a Python function that implements
          preprocessing_fn, optional.
        - labels.CUSTOM_CONFIG: Dictionary of additional parameters for
          preprocessing_fn, optional.
        - labels.DATA_VIEW_LABEL: DataView to be used to read the Example,
          optional
        - labels.FORCE_TF_COMPAT_V1_LABEL: Whether to use TF in compat.v1 mode
          irrespective of installed/enabled TF behaviors.
      outputs: A dictionary of labelled output values, including:
        - labels.PER_SET_STATS_OUTPUT_PATHS_LABEL: Paths to statistics output,
          optional.
        - labels.TRANSFORM_METADATA_OUTPUT_PATH_LABEL: A path to
          TFTransformOutput output.
        - labels.TRANSFORM_MATERIALIZE_OUTPUT_PATHS_LABEL: Paths to transform
          materialization.
        - labels.TEMP_OUTPUT_LABEL: A path to temporary directory.
      status_file: Where the status should be written (not yet implemented)
    """
    del status_file  # unused

    absl.logging.debug(
        'Inputs to executor.Transform function: {}'.format(inputs))
    absl.logging.debug(
        'Outputs to executor.Transform function: {}'.format(outputs))

    compute_statistics = value_utils.GetSoleValue(
        inputs, labels.COMPUTE_STATISTICS_LABEL)
    transform_output_path = value_utils.GetSoleValue(
        outputs, labels.TRANSFORM_METADATA_OUTPUT_PATH_LABEL)
    raw_examples_data_format = value_utils.GetSoleValue(
        inputs, labels.EXAMPLES_DATA_FORMAT_LABEL)
    schema = value_utils.GetSoleValue(inputs, labels.SCHEMA_PATH_LABEL)
    input_dataset_metadata = self._ReadMetadata(raw_examples_data_format,
                                                schema)
    materialize_output_paths = value_utils.GetValues(
        outputs, labels.TRANSFORM_MATERIALIZE_OUTPUT_PATHS_LABEL)
    preprocessing_fn = self._GetPreprocessingFn(inputs, outputs)
    per_set_stats_output_paths = value_utils.GetValues(
        outputs, labels.PER_SET_STATS_OUTPUT_PATHS_LABEL)
    analyze_data_paths = value_utils.GetValues(inputs,
                                               labels.ANALYZE_DATA_PATHS_LABEL)
    analyze_paths_file_formats = value_utils.GetValues(
        inputs, labels.ANALYZE_PATHS_FILE_FORMATS_LABEL)
    transform_data_paths = value_utils.GetValues(
        inputs, labels.TRANSFORM_DATA_PATHS_LABEL)
    transform_paths_file_formats = value_utils.GetValues(
        inputs, labels.TRANSFORM_PATHS_FILE_FORMATS_LABEL)
    input_cache_dir = value_utils.GetSoleValue(
        inputs, labels.CACHE_INPUT_PATH_LABEL, strict=False)
    output_cache_dir = value_utils.GetSoleValue(
        outputs, labels.CACHE_OUTPUT_PATH_LABEL, strict=False)
    per_set_stats_output_paths = value_utils.GetValues(
        outputs, labels.PER_SET_STATS_OUTPUT_PATHS_LABEL)
    temp_path = value_utils.GetSoleValue(outputs, labels.TEMP_OUTPUT_LABEL)
    data_view_uri = value_utils.GetSoleValue(
        inputs, labels.DATA_VIEW_LABEL, strict=False)
    force_tf_compat_v1 = value_utils.GetSoleValue(
        inputs, labels.FORCE_TF_COMPAT_V1_LABEL)

    absl.logging.debug('Force tf.compat.v1: %s', force_tf_compat_v1)
    absl.logging.debug('Analyze data patterns: %s',
                       list(enumerate(analyze_data_paths)))
    absl.logging.debug('Transform data patterns: %s',
                       list(enumerate(transform_data_paths)))
    absl.logging.debug('Transform materialization output paths: %s',
                       list(enumerate(materialize_output_paths)))
    absl.logging.debug('Transform output path: %s', transform_output_path)

    if len(analyze_data_paths) != len(analyze_paths_file_formats):
      raise ValueError(
          'size of analyze_data_paths and '
          'analyze_paths_file_formats do not match: {} v.s {}'.format(
              len(analyze_data_paths), len(analyze_paths_file_formats)))
    if len(transform_data_paths) != len(transform_paths_file_formats):
      raise ValueError(
          'size of transform_data_paths and '
          'transform_paths_file_formats do not match: {} v.s {}'.format(
              len(transform_data_paths), len(transform_paths_file_formats)))

    can_process_analysis_jointly = not bool(output_cache_dir)
    analyze_data_list = self._MakeDatasetList(analyze_data_paths,
                                              analyze_paths_file_formats,
                                              raw_examples_data_format,
                                              data_view_uri,
                                              can_process_analysis_jointly)
    if not analyze_data_list:
      raise ValueError('Analyze data list must not be empty.')

    can_process_transform_jointly = not bool(per_set_stats_output_paths or
                                             materialize_output_paths)
    transform_data_list = self._MakeDatasetList(transform_data_paths,
                                                transform_paths_file_formats,
                                                raw_examples_data_format,
                                                data_view_uri,
                                                can_process_transform_jointly,
                                                per_set_stats_output_paths,
                                                materialize_output_paths)

    all_datasets = analyze_data_list + transform_data_list
    for d in all_datasets:
      d.tfxio = self._CreateTFXIO(d, input_dataset_metadata.schema)
    self._AssertSameTFXIOSchema(all_datasets)
    typespecs = all_datasets[0].tfxio.TensorAdapter().OriginalTypeSpecs()

    # Inspecting the preprocessing_fn even if we know we need a full pass in
    # order to fail faster if it fails.
    analyze_input_columns = tft.get_analyze_input_columns(
        preprocessing_fn, typespecs, force_tf_compat_v1=force_tf_compat_v1)

    if not compute_statistics and not materialize_output_paths:
      if analyze_input_columns:
        absl.logging.warning(
            'Not using the in-place Transform because the following features '
            'require analyzing: {}'.format(
                tuple(c for c in analyze_input_columns)))
      else:
        absl.logging.warning(
            'Using the in-place Transform since compute_statistics=False, '
            'it does not materialize transformed data, and the configured '
            'preprocessing_fn appears to not require analyzing the data.')
        self._RunInPlaceImpl(preprocessing_fn, force_tf_compat_v1,
                             input_dataset_metadata, typespecs,
                             transform_output_path)
        # TODO(b/122478841): Writes status to status file.
        return

    materialization_format = (
        transform_paths_file_formats[-1] if materialize_output_paths else None)
    self._RunBeamImpl(analyze_data_list, transform_data_list, preprocessing_fn,
                      force_tf_compat_v1, input_dataset_metadata,
                      transform_output_path, raw_examples_data_format,
                      temp_path, input_cache_dir, output_cache_dir,
                      compute_statistics, per_set_stats_output_paths,
                      materialization_format, len(analyze_data_paths))