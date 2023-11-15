  def _RunInPlaceImpl(self, preprocessing_fn: Any, force_tf_compat_v1: bool,
                      metadata: dataset_metadata.DatasetMetadata,
                      typespecs: Dict[Text, tf.TypeSpec],
                      transform_output_path: Text) -> _Status:
    """Runs a transformation iteration in-place without looking at the data.

    Args:
      preprocessing_fn: The tf.Transform preprocessing_fn.
      force_tf_compat_v1: If True, call Transform's API to use Tensorflow in
        tf.compat.v1 mode.
      metadata: A DatasetMetadata object for the input data.
      typespecs: a Dict[Text, tf.TypeSpec]
      transform_output_path: An absolute path to write the output to.

    Returns:
      Status of the execution.
    """

    absl.logging.debug('Processing an in-place transform')

    raw_metadata_dir = os.path.join(transform_output_path,
                                    tft.TFTransformOutput.RAW_METADATA_DIR)
    metadata_io.write_metadata(metadata, raw_metadata_dir)
    # TODO(b/149997088): Use typespecs for the tf.compat.v1 path as well.
    feature_specs = schema_utils.schema_as_feature_spec(
        _GetSchemaProto(metadata)).feature_spec
    impl_helper.analyze_in_place(preprocessing_fn, force_tf_compat_v1,
                                 feature_specs, typespecs,
                                 transform_output_path)

    return _Status.OK()