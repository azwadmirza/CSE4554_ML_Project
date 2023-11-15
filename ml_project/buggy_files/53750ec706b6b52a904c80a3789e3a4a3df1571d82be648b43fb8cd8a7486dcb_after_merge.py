    def __init__(self, observation_space, action_space, config):
        config = dict(ray.rllib.agents.dqn.dqn.DEFAULT_CONFIG, **config)
        if not isinstance(action_space, Discrete):
            raise UnsupportedSpaceException(
                "Action space {} is not supported for DQN.".format(
                    action_space))

        self.config = config
        self.cur_epsilon = 1.0
        self.num_actions = action_space.n

        # Action inputs
        self.stochastic = tf.placeholder(tf.bool, (), name="stochastic")
        self.eps = tf.placeholder(tf.float32, (), name="eps")
        self.cur_observations = tf.placeholder(
            tf.float32, shape=(None, ) + observation_space.shape)

        # Action Q network
        with tf.variable_scope(Q_SCOPE) as scope:
            q_values, q_logits, q_dist, _ = self._build_q_network(
                self.cur_observations, observation_space, action_space)
            self.q_values = q_values
            self.q_func_vars = _scope_vars(scope.name)

        # Noise vars for Q network except for layer normalization vars
        if self.config["parameter_noise"]:
            self._build_parameter_noise([
                var for var in self.q_func_vars if "LayerNorm" not in var.name
            ])
            self.action_probs = tf.nn.softmax(self.q_values)

        # Action outputs
        self.output_actions, self.action_prob = self._build_q_value_policy(
            q_values)

        # Replay inputs
        self.obs_t = tf.placeholder(
            tf.float32, shape=(None, ) + observation_space.shape)
        self.act_t = tf.placeholder(tf.int32, [None], name="action")
        self.rew_t = tf.placeholder(tf.float32, [None], name="reward")
        self.obs_tp1 = tf.placeholder(
            tf.float32, shape=(None, ) + observation_space.shape)
        self.done_mask = tf.placeholder(tf.float32, [None], name="done")
        self.importance_weights = tf.placeholder(
            tf.float32, [None], name="weight")

        # q network evaluation
        with tf.variable_scope(Q_SCOPE, reuse=True):
            prev_update_ops = set(tf.get_collection(tf.GraphKeys.UPDATE_OPS))
            q_t, q_logits_t, q_dist_t, model = self._build_q_network(
                self.obs_t, observation_space, action_space)
            q_batchnorm_update_ops = list(
                set(tf.get_collection(tf.GraphKeys.UPDATE_OPS)) -
                prev_update_ops)

        # target q network evalution
        with tf.variable_scope(Q_TARGET_SCOPE) as scope:
            q_tp1, q_logits_tp1, q_dist_tp1, _ = self._build_q_network(
                self.obs_tp1, observation_space, action_space)
            self.target_q_func_vars = _scope_vars(scope.name)

        # q scores for actions which we know were selected in the given state.
        one_hot_selection = tf.one_hot(self.act_t, self.num_actions)
        q_t_selected = tf.reduce_sum(q_t * one_hot_selection, 1)
        q_logits_t_selected = tf.reduce_sum(
            q_logits_t * tf.expand_dims(one_hot_selection, -1), 1)

        # compute estimate of best possible value starting from state at t + 1
        if config["double_q"]:
            with tf.variable_scope(Q_SCOPE, reuse=True):
                q_tp1_using_online_net, q_logits_tp1_using_online_net, \
                    q_dist_tp1_using_online_net, _ = self._build_q_network(
                        self.obs_tp1, observation_space, action_space)
            q_tp1_best_using_online_net = tf.argmax(q_tp1_using_online_net, 1)
            q_tp1_best_one_hot_selection = tf.one_hot(
                q_tp1_best_using_online_net, self.num_actions)
            q_tp1_best = tf.reduce_sum(q_tp1 * q_tp1_best_one_hot_selection, 1)
            q_dist_tp1_best = tf.reduce_sum(
                q_dist_tp1 * tf.expand_dims(q_tp1_best_one_hot_selection, -1),
                1)
        else:
            q_tp1_best_one_hot_selection = tf.one_hot(
                tf.argmax(q_tp1, 1), self.num_actions)
            q_tp1_best = tf.reduce_sum(q_tp1 * q_tp1_best_one_hot_selection, 1)
            q_dist_tp1_best = tf.reduce_sum(
                q_dist_tp1 * tf.expand_dims(q_tp1_best_one_hot_selection, -1),
                1)

        self.loss = self._build_q_loss(q_t_selected, q_logits_t_selected,
                                       q_tp1_best, q_dist_tp1_best)

        # update_target_fn will be called periodically to copy Q network to
        # target Q network
        update_target_expr = []
        assert len(self.q_func_vars) == len(self.target_q_func_vars), \
            (self.q_func_vars, self.target_q_func_vars)
        for var, var_target in zip(self.q_func_vars, self.target_q_func_vars):
            update_target_expr.append(var_target.assign(var))
        self.update_target_expr = tf.group(*update_target_expr)

        # initialize TFPolicyGraph
        self.sess = tf.get_default_session()
        self.loss_inputs = [
            (SampleBatch.CUR_OBS, self.obs_t),
            (SampleBatch.ACTIONS, self.act_t),
            (SampleBatch.REWARDS, self.rew_t),
            (SampleBatch.NEXT_OBS, self.obs_tp1),
            (SampleBatch.DONES, self.done_mask),
            (PRIO_WEIGHTS, self.importance_weights),
        ]
        TFPolicyGraph.__init__(
            self,
            observation_space,
            action_space,
            self.sess,
            obs_input=self.cur_observations,
            action_sampler=self.output_actions,
            action_prob=self.action_prob,
            loss=self.loss.loss,
            model=model,
            loss_inputs=self.loss_inputs,
            update_ops=q_batchnorm_update_ops)
        self.sess.run(tf.global_variables_initializer())