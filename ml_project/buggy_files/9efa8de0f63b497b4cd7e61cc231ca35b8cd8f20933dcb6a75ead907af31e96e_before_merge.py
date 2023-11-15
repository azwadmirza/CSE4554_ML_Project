    def __init__(
            self,
            obs_space: gym.spaces.Space,
            action_space: gym.spaces.Space,
            config: TrainerConfigDict,
            loss_fn: Callable[[
                Policy, ModelV2, Type[TFActionDistribution], SampleBatch
            ], TensorType],
            *,
            stats_fn: Optional[Callable[[Policy, SampleBatch], Dict[
                str, TensorType]]] = None,
            grad_stats_fn: Optional[Callable[[
                Policy, SampleBatch, ModelGradients
            ], Dict[str, TensorType]]] = None,
            before_loss_init: Optional[Callable[[
                Policy, gym.spaces.Space, gym.spaces.Space, TrainerConfigDict
            ], None]] = None,
            make_model: Optional[Callable[[
                Policy, gym.spaces.Space, gym.spaces.Space, TrainerConfigDict
            ], ModelV2]] = None,
            action_sampler_fn: Optional[Callable[[
                TensorType, List[TensorType]
            ], Tuple[TensorType, TensorType]]] = None,
            action_distribution_fn: Optional[Callable[[
                Policy, ModelV2, TensorType, TensorType, TensorType
            ], Tuple[TensorType, type, List[TensorType]]]] = None,
            existing_inputs: Optional[Dict[str, "tf1.placeholder"]] = None,
            existing_model: Optional[ModelV2] = None,
            get_batch_divisibility_req: Optional[Callable[[Policy],
                                                          int]] = None,
            obs_include_prev_action_reward: bool = True):
        """Initialize a dynamic TF policy.

        Args:
            observation_space (gym.spaces.Space): Observation space of the
                policy.
            action_space (gym.spaces.Space): Action space of the policy.
            config (TrainerConfigDict): Policy-specific configuration data.
            loss_fn (Callable[[Policy, ModelV2, Type[TFActionDistribution],
                SampleBatch], TensorType]): Function that returns a loss tensor
                for the policy graph.
            stats_fn (Optional[Callable[[Policy, SampleBatch],
                Dict[str, TensorType]]]): Optional function that returns a dict
                of TF fetches given the policy and batch input tensors.
            grad_stats_fn (Optional[Callable[[Policy, SampleBatch,
                ModelGradients], Dict[str, TensorType]]]):
                Optional function that returns a dict of TF fetches given the
                policy, sample batch, and loss gradient tensors.
            before_loss_init (Optional[Callable[
                [Policy, gym.spaces.Space, gym.spaces.Space,
                TrainerConfigDict], None]]): Optional function to run prior to
                loss init that takes the same arguments as __init__.
            make_model (Optional[Callable[[Policy, gym.spaces.Space,
                gym.spaces.Space, TrainerConfigDict], ModelV2]]): Optional
                function that returns a ModelV2 object given
                policy, obs_space, action_space, and policy config.
                All policy variables should be created in this function. If not
                specified, a default model will be created.
            action_sampler_fn (Optional[Callable[[Policy, ModelV2, Dict[
                str, TensorType], TensorType, TensorType], Tuple[TensorType,
                TensorType]]]): A callable returning a sampled action and its
                log-likelihood given Policy, ModelV2, input_dict, explore,
                timestep, and is_training.
            action_distribution_fn (Optional[Callable[[Policy, ModelV2,
                Dict[str, TensorType], TensorType, TensorType],
                Tuple[TensorType, type, List[TensorType]]]]): A callable
                returning distribution inputs (parameters), a dist-class to
                generate an action distribution object from, and
                internal-state outputs (or an empty list if not applicable).
                Note: No Exploration hooks have to be called from within
                `action_distribution_fn`. It's should only perform a simple
                forward pass through some model.
                If None, pass inputs through `self.model()` to get distribution
                inputs.
                The callable takes as inputs: Policy, ModelV2, input_dict,
                explore, timestep, is_training.
            existing_inputs (Optional[Dict[str, tf1.placeholder]]): When
                copying a policy, this specifies an existing dict of
                placeholders to use instead of defining new ones.
            existing_model (Optional[ModelV2]): When copying a policy, this
                specifies an existing model to clone and share weights with.
            get_batch_divisibility_req (Optional[Callable[[Policy], int]]):
                Optional callable that returns the divisibility requirement for
                sample batches. If None, will assume a value of 1.
            obs_include_prev_action_reward (bool): Whether to include the
                previous action and reward in the model input (default: True).
        """
        self.observation_space = obs_space
        self.action_space = action_space
        self.config = config
        self.framework = "tf"
        self._loss_fn = loss_fn
        self._stats_fn = stats_fn
        self._grad_stats_fn = grad_stats_fn
        self._obs_include_prev_action_reward = obs_include_prev_action_reward

        dist_class = dist_inputs = None
        if action_sampler_fn or action_distribution_fn:
            if not make_model:
                raise ValueError(
                    "`make_model` is required if `action_sampler_fn` OR "
                    "`action_distribution_fn` is given")
        else:
            dist_class, logit_dim = ModelCatalog.get_action_dist(
                action_space, self.config["model"])

        # Setup self.model.
        if existing_model:
            self.model = existing_model
        elif make_model:
            self.model = make_model(self, obs_space, action_space, config)
        else:
            self.model = ModelCatalog.get_model_v2(
                obs_space=obs_space,
                action_space=action_space,
                num_outputs=logit_dim,
                model_config=self.config["model"],
                framework="tf")
        # Auto-update model's inference view requirements, if recurrent.
        self._update_model_inference_view_requirements_from_init_state()

        if existing_inputs:
            self._state_inputs = [
                v for k, v in existing_inputs.items()
                if k.startswith("state_in_")
            ]
            if self._state_inputs:
                self._seq_lens = existing_inputs["seq_lens"]
        else:
            if self.config["_use_trajectory_view_api"]:
                self._state_inputs = [
                    tf1.placeholder(
                        shape=(None, ) + vr.space.shape, dtype=vr.space.dtype)
                    for k, vr in
                    self.model.inference_view_requirements.items()
                    if k[:9] == "state_in_"
                ]
            else:
                self._state_inputs = [
                    tf1.placeholder(shape=(None, ) + s.shape, dtype=s.dtype)
                    for s in self.model.get_initial_state()
                ]

        # Use default settings.
        # Add NEXT_OBS, STATE_IN_0.., and others.
        self.view_requirements = self._get_default_view_requirements()
        # Combine view_requirements for Model and Policy.
        self.view_requirements.update(self.model.inference_view_requirements)

        # Setup standard placeholders.
        if existing_inputs is not None:
            timestep = existing_inputs["timestep"]
            explore = existing_inputs["is_exploring"]
            self._input_dict, self._dummy_batch = \
                self._get_input_dict_and_dummy_batch(
                    self.view_requirements, existing_inputs)
        else:
            action_ph = ModelCatalog.get_action_placeholder(action_space)
            prev_action_ph = ModelCatalog.get_action_placeholder(
                action_space, "prev_action")
            if self.config["_use_trajectory_view_api"]:
                self._input_dict, self._dummy_batch = \
                    self._get_input_dict_and_dummy_batch(
                        self.view_requirements,
                        {SampleBatch.ACTIONS: action_ph,
                         SampleBatch.PREV_ACTIONS: prev_action_ph})
            else:
                self._input_dict = {
                    SampleBatch.CUR_OBS: tf1.placeholder(
                        tf.float32,
                        shape=[None] + list(obs_space.shape),
                        name="observation")
                }
                self._input_dict[SampleBatch.ACTIONS] = action_ph
                if self._obs_include_prev_action_reward:
                    self._input_dict.update({
                        SampleBatch.PREV_ACTIONS: prev_action_ph,
                        SampleBatch.PREV_REWARDS: tf1.placeholder(
                            tf.float32, [None], name="prev_reward"),
                    })
            # Placeholder for (sampling steps) timestep (int).
            timestep = tf1.placeholder(tf.int64, (), name="timestep")
            # Placeholder for `is_exploring` flag.
            explore = tf1.placeholder_with_default(
                True, (), name="is_exploring")

        # Placeholder for RNN time-chunk valid lengths.
        self._seq_lens = tf1.placeholder(
            dtype=tf.int32, shape=[None], name="seq_lens")
        # Placeholder for `is_training` flag.
        self._input_dict["is_training"] = self._get_is_training_placeholder()

        # Create the Exploration object to use for this Policy.
        self.exploration = self._create_exploration()

        # Fully customized action generation (e.g., custom policy).
        if action_sampler_fn:
            sampled_action, sampled_action_logp = action_sampler_fn(
                self,
                self.model,
                obs_batch=self._input_dict[SampleBatch.CUR_OBS],
                state_batches=self._state_inputs,
                seq_lens=self._seq_lens,
                prev_action_batch=self._input_dict.get(
                    SampleBatch.PREV_ACTIONS),
                prev_reward_batch=self._input_dict.get(
                    SampleBatch.PREV_REWARDS),
                explore=explore,
                is_training=self._input_dict["is_training"])
        else:
            # Distribution generation is customized, e.g., DQN, DDPG.
            if action_distribution_fn:
                dist_inputs, dist_class, self._state_out = \
                    action_distribution_fn(
                        self, self.model,
                        obs_batch=self._input_dict[SampleBatch.CUR_OBS],
                        state_batches=self._state_inputs,
                        seq_lens=self._seq_lens,
                        prev_action_batch=self._input_dict.get(
                            SampleBatch.PREV_ACTIONS),
                        prev_reward_batch=self._input_dict.get(
                            SampleBatch.PREV_REWARDS),
                        explore=explore,
                        is_training=self._input_dict["is_training"])
            # Default distribution generation behavior:
            # Pass through model. E.g., PG, PPO.
            else:
                dist_inputs, self._state_out = self.model(
                    self._input_dict, self._state_inputs, self._seq_lens)

            action_dist = dist_class(dist_inputs, self.model)

            # Using exploration to get final action (e.g. via sampling).
            sampled_action, sampled_action_logp = \
                self.exploration.get_exploration_action(
                    action_distribution=action_dist,
                    timestep=timestep,
                    explore=explore)

        # Phase 1 init.
        sess = tf1.get_default_session() or tf1.Session()

        batch_divisibility_req = get_batch_divisibility_req(self) if \
            callable(get_batch_divisibility_req) else \
            (get_batch_divisibility_req or 1)

        super().__init__(
            observation_space=obs_space,
            action_space=action_space,
            config=config,
            sess=sess,
            obs_input=self._input_dict[SampleBatch.OBS],
            action_input=self._input_dict[SampleBatch.ACTIONS],
            sampled_action=sampled_action,
            sampled_action_logp=sampled_action_logp,
            dist_inputs=dist_inputs,
            dist_class=dist_class,
            loss=None,  # dynamically initialized on run
            loss_inputs=[],
            model=self.model,
            state_inputs=self._state_inputs,
            state_outputs=self._state_out,
            prev_action_input=self._input_dict.get(SampleBatch.PREV_ACTIONS),
            prev_reward_input=self._input_dict.get(SampleBatch.PREV_REWARDS),
            seq_lens=self._seq_lens,
            max_seq_len=config["model"]["max_seq_len"],
            batch_divisibility_req=batch_divisibility_req,
            explore=explore,
            timestep=timestep)

        # Phase 2 init.
        if before_loss_init is not None:
            before_loss_init(self, obs_space, action_space, config)

        # Loss initialization and model/postprocessing test calls.
        if not existing_inputs:
            self._initialize_loss_from_dummy_batch(
                auto_remove_unneeded_view_reqs=True)