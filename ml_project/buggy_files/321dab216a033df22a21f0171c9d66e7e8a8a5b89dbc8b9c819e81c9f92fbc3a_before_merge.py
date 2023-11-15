    def __init__(self,
                 model_file,
                 channel=None,
                 max_retrain_num=DEFAULT_MAX_MINIBATCH_RETRAIN_NUM,
                 codec_type=None):
        """
        Arguments:
            model_module: A module to define the model
            channel: grpc channel
            max_retrain_num: max number of a minibatch retrain as its gradients are not accepted by master
        """

        model_module = load_user_model(model_file)
        self._model = model_module.model
        self._feature_columns = model_module.feature_columns()
        self._all_columns = self._feature_columns + model_module.label_columns()
        build_model(self._model, self._feature_columns)
        self._input_fn = model_module.input_fn 
        self._opt_fn = model_module.optimizer
        self._loss = model_module.loss

        if channel is None:
            self._stub = None
        else:
            self._stub = master_pb2_grpc.MasterStub(channel)
        self._max_retrain_num = max_retrain_num
        self._model_version = -1
        self._codec_type = codec_type