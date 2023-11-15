def autolog(every_n_iter=100):
    # pylint: disable=E0611
    """
    Enable automatic logging from TensorFlow to MLflow. If applicable,
    model checkpoints are logged as artifacts to a 'models' directory, along
    with any TensorBoard log data.

    Refer to the tracking documentation for
    information on what is logged with different TensorFlow workflows.

    :param every_n_iter: The frequency with which metrics should be logged.
                                  Defaults to 100. Ex: a value of 100 will log metrics
                                  at step 0, 100, 200, etc.

    """
    global _LOG_EVERY_N_STEPS
    _LOG_EVERY_N_STEPS = every_n_iter

    from distutils.version import StrictVersion

    if StrictVersion(tensorflow.__version__) < StrictVersion('1.12') \
            or StrictVersion(tensorflow.__version__) >= StrictVersion('2.0'):
        warnings.warn("Could not log to MLflow. Only TensorFlow versions" +
                      "1.12 <= v < 2.0.0 are supported.")
        return

    try:
        from tensorflow.python.summary.writer.event_file_writer import EventFileWriter
        from tensorflow.python.summary.writer.event_file_writer_v2 import EventFileWriterV2
        from tensorflow.python.saved_model import tag_constants
        from tensorflow.python.summary.writer.writer import FileWriter
    except ImportError:
        warnings.warn("Could not log to MLflow. Only TensorFlow versions" +
                      "1.12 <= v < 2.0.0 are supported.")
        return

    @gorilla.patch(tensorflow.estimator.Estimator)
    def export_saved_model(self, *args, **kwargs):
        original = gorilla.get_original_attribute(tensorflow.estimator.Estimator,
                                                  'export_saved_model')
        serialized = original(self, *args, **kwargs)
        try:
            log_model(tf_saved_model_dir=serialized.decode('utf-8'),
                      tf_meta_graph_tags=[tag_constants.SERVING],
                      tf_signature_def_key='predict',
                      artifact_path='model')
        except MlflowException as e:
            warnings.warn("Logging to MLflow failed: " + str(e))
        return serialized

    @gorilla.patch(tensorflow.estimator.Estimator)
    def export_savedmodel(self, *args, **kwargs):
        original = gorilla.get_original_attribute(tensorflow.estimator.Estimator,
                                                  'export_savedmodel')
        serialized = original(self, *args, **kwargs)
        try:
            log_model(tf_saved_model_dir=serialized.decode('utf-8'),
                      tf_meta_graph_tags=[tag_constants.SERVING],
                      tf_signature_def_key='predict',
                      artifact_path='model')
        except MlflowException as e:
            warnings.warn("Logging to MLflow failed: " + str(e))
        return serialized

    @gorilla.patch(tensorflow.keras.Model)
    def fit(self, *args, **kwargs):
        original = gorilla.get_original_attribute(tensorflow.keras.Model, 'fit')
        if len(args) >= 6:
            l = list(args)
            l[5], log_dir = _setup_callbacks(l[5])
            args = tuple(l)
        elif 'callbacks' in kwargs:
            kwargs['callbacks'], log_dir = _setup_callbacks(kwargs['callbacks'])
        else:
            kwargs['callbacks'], log_dir = _setup_callbacks([])
        result = original(self, *args, **kwargs)
        _flush_queue()
        _log_artifacts_with_warning(local_dir=log_dir, artifact_path='tensorboard_logs')
        shutil.rmtree(log_dir)
        return result

    @gorilla.patch(EventFileWriter)
    def add_event(self, event):
        _log_event(event)
        original = gorilla.get_original_attribute(EventFileWriter, 'add_event')
        return original(self, event)

    @gorilla.patch(FileWriter)
    def add_summary(self, *args, **kwargs):
        original = gorilla.get_original_attribute(FileWriter, 'add_summary')
        result = original(self, *args, **kwargs)
        _flush_queue()
        return result

    settings = gorilla.Settings(allow_hit=True, store_hit=True)
    patches = [
        gorilla.Patch(EventFileWriter, 'add_event', add_event, settings=settings),
        gorilla.Patch(EventFileWriterV2, 'add_event', add_event, settings=settings),
        gorilla.Patch(tensorflow.keras.Model, 'fit', fit, settings=settings),
        gorilla.Patch(tensorflow.estimator.Estimator, 'export_saved_model',
                      export_saved_model, settings=settings),
        gorilla.Patch(tensorflow.estimator.Estimator, 'export_savedmodel',
                      export_savedmodel, settings=settings),
        gorilla.Patch(FileWriter, 'add_summary', add_summary, settings=settings),
        ]

    for x in patches:
        gorilla.apply(x)