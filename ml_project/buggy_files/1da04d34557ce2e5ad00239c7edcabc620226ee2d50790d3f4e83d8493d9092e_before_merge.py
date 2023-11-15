    def __init__(self,
                 observation_space: gym.spaces.Space,
                 action_space: gym.spaces.Space,
                 config: TrainerConfigDict,
                 sess: "tf1.Session",
                 obs_input: TensorType,
                 sampled_action: TensorType,
                 loss: TensorType,
                 loss_inputs: List[Tuple[str, TensorType]],
                 model: ModelV2 = None,
                 sampled_action_logp: Optional[TensorType] = None,
                 action_input: Optional[TensorType] = None,
                 log_likelihood: Optional[TensorType] = None,
                 dist_inputs: Optional[TensorType] = None,
                 dist_class: Optional[type] = None,
                 state_inputs: Optional[List[TensorType]] = None,
                 state_outputs: Optional[List[TensorType]] = None,
                 prev_action_input: Optional[TensorType] = None,
                 prev_reward_input: Optional[TensorType] = None,
                 seq_lens: Optional[TensorType] = None,
                 max_seq_len: int = 20,
                 batch_divisibility_req: int = 1,
                 update_ops: List[TensorType] = None,
                 explore: Optional[TensorType] = None,
                 timestep: Optional[TensorType] = None):
        """Initializes a Policy object.

        Args:
            observation_space (gym.spaces.Space): Observation space of the env.
            action_space (gym.spaces.Space): Action space of the env.
            config (TrainerConfigDict): The Policy config dict.
            sess (tf1.Session): The TensorFlow session to use.
            obs_input (TensorType): Input placeholder for observations, of
                shape [BATCH_SIZE, obs...].
            sampled_action (TensorType): Tensor for sampling an action, of
                shape [BATCH_SIZE, action...]
            loss (TensorType): Scalar policy loss output tensor.
            loss_inputs (List[Tuple[str, TensorType]]): A (name, placeholder)
                tuple for each loss input argument. Each placeholder name must
                correspond to a SampleBatch column key returned by
                postprocess_trajectory(), and has shape [BATCH_SIZE, data...].
                These keys will be read from postprocessed sample batches and
                fed into the specified placeholders during loss computation.
            model (ModelV2): used to integrate custom losses and
                stats from user-defined RLlib models.
            sampled_action_logp (Optional[TensorType]): log probability of the
                sampled action.
            action_input (Optional[TensorType]): Input placeholder for actions
                for logp/log-likelihood calculations.
            log_likelihood (Optional[TensorType]): Tensor to calculate the
                log_likelihood (given action_input and obs_input).
            dist_class (Optional[type]): An optional ActionDistribution class
                to use for generating a dist object from distribution inputs.
            dist_inputs (Optional[TensorType]): Tensor to calculate the
                distribution inputs/parameters.
            state_inputs (Optional[List[TensorType]]): List of RNN state input
                Tensors.
            state_outputs (Optional[List[TensorType]]): List of RNN state
                output Tensors.
            prev_action_input (Optional[TensorType]): placeholder for previous
                actions.
            prev_reward_input (Optional[TensorType]): placeholder for previous
                rewards.
            seq_lens (Optional[TensorType]): Placeholder for RNN sequence
                lengths, of shape [NUM_SEQUENCES].
                Note that NUM_SEQUENCES << BATCH_SIZE. See
                policy/rnn_sequencing.py for more information.
            max_seq_len (int): Max sequence length for LSTM training.
            batch_divisibility_req (int): pad all agent experiences batches to
                multiples of this value. This only has an effect if not using
                a LSTM model.
            update_ops (List[TensorType]): override the batchnorm update ops to
                run when applying gradients. Otherwise we run all update ops
                found in the current variable scope.
            explore (Optional[TensorType]): Placeholder for `explore` parameter
                into call to Exploration.get_exploration_action.
            timestep (Optional[TensorType]): Placeholder for the global
                sampling timestep.
        """
        self.framework = "tf"
        super().__init__(observation_space, action_space, config)
        # Disable env-info placeholder.
        if SampleBatch.INFOS in self.view_requirements:
            self.view_requirements[SampleBatch.INFOS].used_for_training = False

        assert model is None or isinstance(model, ModelV2), \
            "Model classes for TFPolicy other than `ModelV2` not allowed! " \
            "You passed in {}.".format(model)
        self.model = model
        # Auto-update model's inference view requirements, if recurrent.
        if self.model is not None:
            self._update_model_inference_view_requirements_from_init_state()

        self.exploration = self._create_exploration()
        self._sess = sess
        self._obs_input = obs_input
        self._prev_action_input = prev_action_input
        self._prev_reward_input = prev_reward_input
        self._sampled_action = sampled_action
        self._is_training = self._get_is_training_placeholder()
        self._is_exploring = explore if explore is not None else \
            tf1.placeholder_with_default(True, (), name="is_exploring")
        self._sampled_action_logp = sampled_action_logp
        self._sampled_action_prob = (tf.math.exp(self._sampled_action_logp)
                                     if self._sampled_action_logp is not None
                                     else None)
        self._action_input = action_input  # For logp calculations.
        self._dist_inputs = dist_inputs
        self.dist_class = dist_class

        self._state_inputs = state_inputs or []
        self._state_outputs = state_outputs or []
        self._seq_lens = seq_lens
        self._max_seq_len = max_seq_len
        if len(self._state_inputs) != len(self._state_outputs):
            raise ValueError(
                "Number of state input and output tensors must match, got: "
                "{} vs {}".format(self._state_inputs, self._state_outputs))
        if len(self.get_initial_state()) != len(self._state_inputs):
            raise ValueError(
                "Length of initial state must match number of state inputs, "
                "got: {} vs {}".format(self.get_initial_state(),
                                       self._state_inputs))
        if self._state_inputs and self._seq_lens is None:
            raise ValueError(
                "seq_lens tensor must be given if state inputs are defined")

        self._batch_divisibility_req = batch_divisibility_req
        self._update_ops = update_ops
        self._apply_op = None
        self._stats_fetches = {}
        self._timestep = timestep if timestep is not None else \
            tf1.placeholder(tf.int64, (), name="timestep")

        self._optimizer = None
        self._grads_and_vars = None
        self._grads = None
        # Policy tf-variables (weights), whose values to get/set via
        # get_weights/set_weights.
        self._variables = None
        # Local optimizer's tf-variables (e.g. state vars for Adam).
        # Will be stored alongside `self._variables` when checkpointing.
        self._optimizer_variables = None

        # The loss tf-op.
        self._loss = None
        # A batch dict passed into loss function as input.
        self._loss_input_dict = {}
        if loss is not None:
            self._initialize_loss(loss, loss_inputs)

        # The log-likelihood calculator op.
        self._log_likelihood = log_likelihood
        if self._log_likelihood is None and self._dist_inputs is not None and \
                self.dist_class is not None:
            self._log_likelihood = self.dist_class(
                self._dist_inputs, self.model).logp(self._action_input)