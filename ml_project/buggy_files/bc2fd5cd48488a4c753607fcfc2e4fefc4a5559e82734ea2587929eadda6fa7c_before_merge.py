  def _RunInPlaceImpl(
      self, preprocessing_fn: Any,
      metadata: dataset_metadata.DatasetMetadata,
      typespecs: Dict[Text, tf.TypeSpec],
      transform_output_path: Text) -> _Status:
    """Runs a transformation iteration in-place without looking at the data.

    Args:
      preprocessing_fn: The tf.Transform preprocessing_fn.
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

    with tf.compat.v1.Graph().as_default() as graph:
      with tf.compat.v1.Session(graph=graph) as sess:

        input_signature = impl_helper.batched_placeholders_from_specs(
            schema_utils.schema_as_feature_spec(
                _GetSchemaProto(metadata)).feature_spec)

        # In order to avoid a bug where import_graph_def fails when the
        # input_map and return_elements of an imported graph are the same
        # (b/34288791), we avoid using the placeholder of an input column as an
        # output of a graph. We do this by applying tf.identity to all inputs of
        # the preprocessing_fn.  Note this applies at the level of raw tensors.
        # TODO(b/34288791): Remove this workaround and use a shallow copy of
        # inputs instead.  A shallow copy is needed in case
        # self._preprocessing_fn mutates its input.
        copied_inputs = impl_helper.copy_tensors(input_signature)

        output_signature = preprocessing_fn(copied_inputs)
        sess.run(tf.compat.v1.global_variables_initializer())
        sess.run(tf.compat.v1.tables_initializer())
        transform_fn_path = os.path.join(transform_output_path,
                                         tft.TFTransformOutput.TRANSFORM_FN_DIR)
        saved_transform_io.write_saved_transform_from_session(
            sess, input_signature, output_signature, transform_fn_path)

        transformed_metadata = dataset_metadata.DatasetMetadata(
            schema=tft.schema_inference.infer_feature_schema(
                output_signature, graph, sess))

    transformed_metadata_dir = os.path.join(
        transform_output_path, tft.TFTransformOutput.TRANSFORMED_METADATA_DIR)
    metadata_io.write_metadata(transformed_metadata, transformed_metadata_dir)

    return _Status.OK()