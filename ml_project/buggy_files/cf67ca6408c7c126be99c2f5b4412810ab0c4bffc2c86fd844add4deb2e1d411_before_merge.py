  def _RunBeamImpl(self, analyze_data_list: List[_Dataset],
                   transform_data_list: List[_Dataset], preprocessing_fn: Any,
                   input_dataset_metadata: dataset_metadata.DatasetMetadata,
                   transform_output_path: Text, raw_examples_data_format: int,
                   temp_path: Text, input_cache_dir: Optional[Text],
                   output_cache_dir: Optional[Text], compute_statistics: bool,
                   per_set_stats_output_paths: Sequence[Text],
                   materialization_format: Optional[Text],
                   analyze_paths_count: int) -> _Status:
    """Perform data preprocessing with TFT.

    Args:
      analyze_data_list: List of datasets for analysis.
      transform_data_list: List of datasets for transform.
      preprocessing_fn: The tf.Transform preprocessing_fn.
      input_dataset_metadata: A DatasetMetadata object for the input data.
      transform_output_path: An absolute path to write the output to.
      raw_examples_data_format: The data format of the raw examples. One of the
        enums from example_gen_pb2.PayloadFormat.
      temp_path: A path to a temporary dir.
      input_cache_dir: A dir containing the input analysis cache. May be None.
      output_cache_dir: A dir to write the analysis cache to. May be None.
      compute_statistics: A bool indicating whether or not compute statistics.
      per_set_stats_output_paths: Paths to per-set statistics output. If empty,
        per-set statistics is not produced.
      materialization_format: A string describing the format of the materialized
        data or None if materialization is not enabled.
      analyze_paths_count: An integer, the number of paths that should be used
        for analysis.

    Returns:
      Status of the execution.
    """
    self._AssertSameTFXIOSchema(analyze_data_list)
    unprojected_typespecs = (
        analyze_data_list[0].tfxio.TensorAdapter().OriginalTypeSpecs())

    analyze_input_columns = tft.get_analyze_input_columns(
        preprocessing_fn, unprojected_typespecs)
    transform_input_columns = tft.get_transform_input_columns(
        preprocessing_fn, unprojected_typespecs)
    # Use the same dataset (same columns) for AnalyzeDataset and computing
    # pre-transform stats so that the data will only be read once for these
    # two operations.
    if compute_statistics:
      analyze_input_columns = list(
          set(list(analyze_input_columns) + list(transform_input_columns)))

    for d in analyze_data_list:
      d.tfxio = d.tfxio.Project(analyze_input_columns)

    self._AssertSameTFXIOSchema(analyze_data_list)
    analyze_data_tensor_adapter_config = (
        analyze_data_list[0].tfxio.TensorAdapterConfig())

    for d in transform_data_list:
      d.tfxio = d.tfxio.Project(transform_input_columns)

    desired_batch_size = self._GetDesiredBatchSize(raw_examples_data_format)

    with self._CreatePipeline(transform_output_path) as pipeline:
      with tft_beam.Context(
          temp_dir=temp_path,
          desired_batch_size=desired_batch_size,
          passthrough_keys=self._GetTFXIOPassthroughKeys(),
          use_deep_copy_optimization=True,
          use_tfxio=True):
        # pylint: disable=expression-not-assigned
        # pylint: disable=no-value-for-parameter
        _ = (
            pipeline
            | 'IncrementPipelineMetrics' >> self._IncrementPipelineMetrics(
                len(unprojected_typespecs), len(analyze_input_columns),
                len(transform_input_columns), analyze_paths_count))

        (new_analyze_data_dict, input_cache) = (
            pipeline
            | 'OptimizeRun' >> self._OptimizeRun(
                input_cache_dir, output_cache_dir, analyze_data_list,
                unprojected_typespecs, preprocessing_fn,
                self._GetCacheSource()))

        if input_cache:
          absl.logging.debug('Analyzing data with cache.')

        full_analyze_dataset_keys_list = [
            dataset.dataset_key for dataset in analyze_data_list
        ]

        # Removing unneeded datasets if they won't be needed for statistics or
        # materialization.
        if materialization_format is None and not compute_statistics:
          if None in new_analyze_data_dict.values():
            absl.logging.debug(
                'Not reading the following datasets due to cache: %s', [
                    dataset.file_pattern
                    for dataset in analyze_data_list
                    if new_analyze_data_dict[dataset.dataset_key] is None
                ])
          analyze_data_list = [
              d for d in new_analyze_data_dict.values() if d is not None
          ]

        for dataset in analyze_data_list:
          infix = 'AnalysisIndex{}'.format(dataset.index)
          dataset.standardized = (
              pipeline
              | 'TFXIOReadAndDecode[{}]'.format(infix) >>
              dataset.tfxio.BeamSource(desired_batch_size))

        input_analysis_data = {}
        for key, dataset in new_analyze_data_dict.items():
          input_analysis_data[key] = (
              None if dataset is None else dataset.standardized)

        transform_fn, cache_output = (
            (input_analysis_data, input_cache,
             analyze_data_tensor_adapter_config)
            | 'Analyze' >> tft_beam.AnalyzeDatasetWithCache(
                preprocessing_fn, pipeline=pipeline))

        # Write the raw/input metadata.
        (input_dataset_metadata
         | 'WriteMetadata' >> tft_beam.WriteMetadata(
             os.path.join(transform_output_path,
                          tft.TFTransformOutput.RAW_METADATA_DIR), pipeline))

        # WriteTransformFn writes transform_fn and metadata to subdirectories
        # tensorflow_transform.SAVED_MODEL_DIR and
        # tensorflow_transform.TRANSFORMED_METADATA_DIR respectively.
        (transform_fn
         | 'WriteTransformFn'
         >> tft_beam.WriteTransformFn(transform_output_path))

        if output_cache_dir is not None and cache_output is not None:
          tf.io.gfile.makedirs(output_cache_dir)
          absl.logging.debug('Using existing cache in: %s', input_cache_dir)
          if input_cache_dir is not None:
            # Only copy cache that is relevant to this iteration. This is
            # assuming that this pipeline operates on rolling ranges, so those
            # cache entries may also be relevant for future iterations.
            for span_cache_dir in input_analysis_data:
              full_span_cache_dir = os.path.join(input_cache_dir,
                                                 span_cache_dir.key)
              if tf.io.gfile.isdir(full_span_cache_dir):
                self._CopyCache(
                    full_span_cache_dir,
                    os.path.join(output_cache_dir, span_cache_dir.key))

          (cache_output
           | 'WriteCache' >> analyzer_cache.WriteAnalysisCacheToFS(
               pipeline=pipeline,
               cache_base_dir=output_cache_dir,
               sink=self._GetCacheSink(),
               dataset_keys=full_analyze_dataset_keys_list))

        if compute_statistics or materialization_format is not None:
          # Do not compute pre-transform stats if the input format is raw proto,
          # as StatsGen would treat any input as tf.Example. Note that
          # tf.SequenceExamples are wire-format compatible with tf.Examples.
          if (compute_statistics and
              not self._IsDataFormatProto(raw_examples_data_format)):
            # Aggregated feature stats before transformation.
            pre_transform_feature_stats_path = os.path.join(
                transform_output_path,
                tft.TFTransformOutput.PRE_TRANSFORM_FEATURE_STATS_PATH)

            if self._IsDataFormatSequenceExample(raw_examples_data_format):
              schema_proto = None
            else:
              schema_proto = _GetSchemaProto(input_dataset_metadata)

            if self._IsDataFormatSequenceExample(raw_examples_data_format):
              def _ExtractRawExampleBatches(record_batch):
                return record_batch.column(
                    record_batch.schema.get_field_index(
                        RAW_EXAMPLE_KEY)).flatten().to_pylist()
              # Make use of the fact that tf.SequenceExample is wire-format
              # compatible with tf.Example
              stats_input = []
              for dataset in analyze_data_list:
                infix = 'AnalysisIndex{}'.format(dataset.index)
                stats_input.append(
                    dataset.standardized
                    | 'ExtractRawExampleBatches[{}]'.format(infix) >> beam.Map(
                        _ExtractRawExampleBatches)
                    | 'DecodeSequenceExamplesAsExamplesIntoRecordBatches[{}]'
                    .format(infix) >> beam.ParDo(
                        self._ToArrowRecordBatchesFn(schema_proto)))
            else:
              stats_input = [
                  dataset.standardized for dataset in analyze_data_list]

            pre_transform_stats_options = (
                transform_stats_options.get_pre_transform_stats_options())
            (stats_input
             | 'FlattenAnalysisDatasets' >> beam.Flatten(pipeline=pipeline)
             | 'GenerateStats[FlattenedAnalysisDataset]' >> self._GenerateStats(
                 pre_transform_feature_stats_path,
                 schema_proto,
                 stats_options=pre_transform_stats_options))

          # transform_data_list is a superset of analyze_data_list, we pay the
          # cost to read the same dataset (analyze_data_list) again here to
          # prevent certain beam runner from doing large temp materialization.
          for dataset in transform_data_list:
            infix = 'TransformIndex{}'.format(dataset.index)
            dataset.standardized = (
                pipeline | 'TFXIOReadAndDecode[{}]'.format(infix) >>
                dataset.tfxio.BeamSource(desired_batch_size))
            (dataset.transformed, metadata) = (
                ((dataset.standardized, dataset.tfxio.TensorAdapterConfig()),
                 transform_fn)
                | 'Transform[{}]'.format(infix) >> tft_beam.TransformDataset())

            dataset.transformed_and_serialized = (
                dataset.transformed
                | 'EncodeAndSerialize[{}]'.format(infix)
                >> beam.ParDo(self._EncodeAsSerializedExamples(),
                              _GetSchemaProto(metadata)))

          if compute_statistics:
            # Aggregated feature stats after transformation.
            _, metadata = transform_fn

            # TODO(b/70392441): Retain tf.Metadata (e.g., IntDomain) in
            # schema. Currently input dataset schema only contains dtypes,
            # and other metadata is dropped due to roundtrip to tensors.
            transformed_schema_proto = _GetSchemaProto(metadata)

            for dataset in transform_data_list:
              infix = 'TransformIndex{}'.format(dataset.index)
              dataset.transformed_and_standardized = (
                  dataset.transformed_and_serialized
                  | 'FromTransformedToArrowRecordBatches[{}]'
                  .format(infix)
                  >> self._ToArrowRecordBatches(
                      schema=transformed_schema_proto))

            post_transform_feature_stats_path = os.path.join(
                transform_output_path,
                tft.TFTransformOutput.POST_TRANSFORM_FEATURE_STATS_PATH)

            post_transform_stats_options = (
                transform_stats_options.get_post_transform_stats_options())
            ([dataset.transformed_and_standardized
              for dataset in transform_data_list]
             | 'FlattenTransformedDatasets' >> beam.Flatten()
             | 'GenerateStats[FlattenedTransformedDatasets]' >>
             self._GenerateStats(
                 post_transform_feature_stats_path,
                 transformed_schema_proto,
                 stats_options=post_transform_stats_options))

            if per_set_stats_output_paths:
              # TODO(b/130885503): Remove duplicate stats gen compute that is
              # done both on a flattened view of the data, and on each span
              # below.
              for dataset in transform_data_list:
                infix = 'TransformIndex{}'.format(dataset.index)
                (dataset.transformed_and_standardized
                 | 'GenerateStats[{}]'.format(infix) >> self._GenerateStats(
                     dataset.stats_output_path,
                     transformed_schema_proto,
                     stats_options=post_transform_stats_options))

          if materialization_format is not None:
            for dataset in transform_data_list:
              infix = 'TransformIndex{}'.format(dataset.index)
              (dataset.transformed_and_serialized
               | 'Materialize[{}]'.format(infix) >> self._WriteExamples(
                   materialization_format,
                   dataset.materialize_output_path))

    return _Status.OK()