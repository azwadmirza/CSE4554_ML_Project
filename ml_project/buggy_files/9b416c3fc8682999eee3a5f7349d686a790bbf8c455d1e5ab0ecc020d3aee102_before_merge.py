  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]) -> None:
    """Push model to target directory if blessed.

    Args:
      input_dict: Input dict from input key to a list of artifacts, including:
        - model_export: exported model from trainer.
        - model_blessing: model blessing path from model_validator.  A push
          action delivers the model exports produced by Trainer to the
          destination defined in component config.
      output_dict: Output dict from key to a list of artifacts, including:
        - model_push: A list of 'ModelPushPath' artifact of size one. It will
          include the model in this push execution if the model was pushed.
      exec_properties: A dict of execution properties, including:
        - push_destination: JSON string of pusher_pb2.PushDestination instance,
          providing instruction of destination to push model.

    Returns:
      None
    """
    self._log_startup(input_dict, output_dict, exec_properties)
    model_push = artifact_utils.get_single_instance(
        output_dict[PUSHED_MODEL_KEY])
    if not self.CheckBlessing(input_dict):
      model_push.set_int_custom_property('pushed', 0)
      return
    model_push_uri = model_push.uri
    model_export = artifact_utils.get_single_instance(input_dict[MODEL_KEY])
    model_export_uri = model_export.uri
    logging.info('Model pushing.')
    # Copy the model to pushing uri.
    model_path = path_utils.serving_model_path(model_export_uri)
    model_version = path_utils.get_serving_model_version(model_export_uri)
    logging.info('Model version is %s', model_version)
    io_utils.copy_dir(model_path, os.path.join(model_push_uri, model_version))
    logging.info('Model written to %s.', model_push_uri)

    # Copied to a fixed outside path, which can be listened by model server.
    #
    # If model is already successfully copied to outside before, stop copying.
    # This is because model validator might blessed same model twice (check
    # mv driver) with different blessing output, we still want Pusher to
    # handle the mv output again to keep metadata tracking, but no need to
    # copy to outside path again..
    # TODO(jyzhao): support rpc push and verification.
    push_destination = pusher_pb2.PushDestination()
    json_format.Parse(exec_properties['push_destination'], push_destination)
    serving_path = os.path.join(push_destination.filesystem.base_directory,
                                model_version)
    if tf.io.gfile.exists(serving_path):
      logging.info(
          'Destination directory %s already exists, skipping current push.',
          serving_path)
    else:
      # tf.serving won't load partial model, it will retry until fully copied.
      io_utils.copy_dir(model_path, serving_path)
      logging.info('Model written to serving path %s.', serving_path)

    model_push.set_int_custom_property('pushed', 1)
    model_push.set_string_custom_property('pushed_model', model_export_uri)
    model_push.set_int_custom_property('pushed_model_id', model_export.id)
    logging.info('Model pushed to %s.', serving_path)