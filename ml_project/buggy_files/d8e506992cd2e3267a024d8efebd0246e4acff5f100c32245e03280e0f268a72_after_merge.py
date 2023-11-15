  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]) -> None:
    """TensorFlow Transform executor entrypoint.

    This implements BaseExecutor.Do() and is invoked by orchestration systems.
    This is not inteded for manual usage or further customization. Please use
    the Transform() function which takes an input format with no artifact
    dependency.

    Args:
      input_dict: Input dict from input key to a list of artifacts, including:
        - input_data: A list of type `standard_artifacts.Examples` which should
          contain custom splits specified in splits_config. If custom split is
          not provided, this should contain two splits 'train' and 'eval'.
        - schema: A list of type `standard_artifacts.Schema` which should
          contain a single schema artifact.
        - analyzer_cache: Cache input of 'tf.Transform', where cached
          information for analyzed examples from previous runs will be read.
      output_dict: Output dict from key to a list of artifacts, including:
        - transform_output: Output of 'tf.Transform', which includes an exported
          Tensorflow graph suitable for both training and serving;
        - transformed_examples: Materialized transformed examples, which
          includes transform splits as specified in splits_config. If custom
          split is not provided, this should include both 'train' and 'eval'
          splits.
        - updated_analyzer_cache: Cache output of 'tf.Transform', where
          cached information for analyzed examples will be written.
      exec_properties: A dict of execution properties, including:
        - module_file: The file path to a python module file, from which the
          'preprocessing_fn' function will be loaded.
        - preprocessing_fn: The module path to a python function that
          implements 'preprocessing_fn'. Exactly one of 'module_file' and
          'preprocessing_fn' should be set.
        - splits_config: A transform_pb2.SplitsConfig instance, providing splits
          that should be analyzed and splits that should be transformed. Note
          analyze and transform splits can have overlap. Default behavior (when
          splits_config is not set) is analyze the 'train' split and transform
          all splits. If splits_config is set, analyze cannot be empty.

    Returns:
      None
    """
    self._log_startup(input_dict, output_dict, exec_properties)

    splits_config = transform_pb2.SplitsConfig()
    if exec_properties.get('splits_config', None):
      json_format.Parse(exec_properties['splits_config'], splits_config)
      if not splits_config.analyze:
        raise ValueError('analyze cannot be empty when splits_config is set.')
    else:
      splits_config.analyze.append('train')

      # All input artifacts should have the same set of split names.
      split_names = artifact_utils.decode_split_names(
          input_dict[EXAMPLES_KEY][0].split_names)
      split_names_set = set(split_names)

      for artifact in input_dict[EXAMPLES_KEY]:
        artifact_split_names = artifact_utils.decode_split_names(
            artifact.split_names)
        if split_names_set != set(artifact_split_names):
          raise ValueError(
              'Not all input artifacts have the same split names: (%s, %s)' %
              (split_names, artifact_split_names))

      splits_config.transform.extend(split_names)
      absl.logging.info(
          "Analyze the 'train' split and transform all splits when "
          'splits_config is not set.')

    payload_format, data_view_uri = (
        tfxio_utils.resolve_payload_format_and_data_view_uri(
            input_dict[EXAMPLES_KEY]))
    schema_file = io_utils.get_only_uri_in_dir(
        artifact_utils.get_single_uri(input_dict[SCHEMA_KEY]))
    transform_output = artifact_utils.get_single_uri(
        output_dict[TRANSFORM_GRAPH_KEY])

    temp_path = os.path.join(transform_output, _TEMP_DIR_IN_TRANSFORM_OUTPUT)
    absl.logging.debug('Using temp path %s for tft.beam', temp_path)

    analyze_data_paths = []
    for split in splits_config.analyze:
      data_uris = artifact_utils.get_split_uris(input_dict[EXAMPLES_KEY], split)
      for data_uri in data_uris:
        analyze_data_paths.append(io_utils.all_files_pattern(data_uri))

    transform_data_paths = []
    materialize_output_paths = []
    if output_dict.get(TRANSFORMED_EXAMPLES_KEY) is not None:
      for transformed_example_artifact in output_dict[TRANSFORMED_EXAMPLES_KEY]:
        transformed_example_artifact.split_names = (
            artifact_utils.encode_split_names(list(splits_config.transform)))

      for split in splits_config.transform:
        data_uris = artifact_utils.get_split_uris(input_dict[EXAMPLES_KEY],
                                                  split)
        for data_uri in data_uris:
          transform_data_paths.append(io_utils.all_files_pattern(data_uri))

        transformed_example_uris = artifact_utils.get_split_uris(
            output_dict[TRANSFORMED_EXAMPLES_KEY], split)
        for output_uri in transformed_example_uris:
          materialize_output_paths.append(
              os.path.join(output_uri, _DEFAULT_TRANSFORMED_EXAMPLES_PREFIX))

    def _GetCachePath(label, params_dict):
      if params_dict.get(label) is None:
        return None
      else:
        return artifact_utils.get_single_uri(params_dict[label])

    label_inputs = {
        labels.COMPUTE_STATISTICS_LABEL:
            False,
        labels.SCHEMA_PATH_LABEL:
            schema_file,
        labels.EXAMPLES_DATA_FORMAT_LABEL:
            payload_format,
        labels.DATA_VIEW_LABEL:
            data_view_uri,
        labels.ANALYZE_DATA_PATHS_LABEL:
            analyze_data_paths,
        labels.ANALYZE_PATHS_FILE_FORMATS_LABEL: [labels.FORMAT_TFRECORD] *
                                                 len(analyze_data_paths),
        labels.TRANSFORM_DATA_PATHS_LABEL:
            transform_data_paths,
        labels.TRANSFORM_PATHS_FILE_FORMATS_LABEL: [labels.FORMAT_TFRECORD] *
                                                   len(transform_data_paths),
        labels.MODULE_FILE:
            exec_properties.get('module_file', None),
        labels.PREPROCESSING_FN:
            exec_properties.get('preprocessing_fn', None),
        labels.CUSTOM_CONFIG:
            exec_properties.get('custom_config', None),
        labels.FORCE_TF_COMPAT_V1_LABEL:
            True,
    }
    cache_input = _GetCachePath(ANALYZER_CACHE_KEY, input_dict)
    if cache_input is not None:
      label_inputs[labels.CACHE_INPUT_PATH_LABEL] = cache_input

    label_outputs = {
        labels.TRANSFORM_METADATA_OUTPUT_PATH_LABEL: transform_output,
        labels.TRANSFORM_MATERIALIZE_OUTPUT_PATHS_LABEL:
            materialize_output_paths,
        labels.TEMP_OUTPUT_LABEL: str(temp_path),
    }
    cache_output = _GetCachePath(UPDATED_ANALYZER_CACHE_KEY, output_dict)
    if cache_output is not None:
      label_outputs[labels.CACHE_OUTPUT_PATH_LABEL] = cache_output
    status_file = 'status_file'  # Unused
    self.Transform(label_inputs, label_outputs, status_file)
    absl.logging.debug('Cleaning up temp path %s on executor success',
                       temp_path)
    io_utils.delete_dir(temp_path)