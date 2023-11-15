    def __init__(self,
                 obs_space,
                 action_space,
                 num_outputs,
                 model_config,
                 name,
                 q_hiddens=(256, ),
                 dueling=False,
                 num_atoms=1,
                 use_noisy=False,
                 v_min=-10.0,
                 v_max=10.0,
                 sigma0=0.5,
                 parameter_noise=False):
        """Initialize variables of this model.

        Extra model kwargs:
            q_hiddens (list): defines size of hidden layers for the q head.
                These will be used to postprocess the model output for the
                purposes of computing Q values.
            dueling (bool): whether to build the state value head for DDQN
            num_atoms (int): if >1, enables distributional DQN
            use_noisy (bool): use noisy nets
            v_min (float): min value support for distributional DQN
            v_max (float): max value support for distributional DQN
            sigma0 (float): initial value of noisy nets
            parameter_noise (bool): enable layer norm for param noise

        Note that the core layers for forward() are not defined here, this
        only defines the layers for the Q head. Those layers for forward()
        should be defined in subclasses of DistributionalQModel.
        """

        super(DistributionalQModel, self).__init__(
            obs_space, action_space, num_outputs, model_config, name)

        # setup the Q head output (i.e., model for get_q_values)
        self.model_out = tf.keras.layers.Input(
            shape=(num_outputs, ), name="model_out")

        def build_action_value(model_out):
            if q_hiddens:
                action_out = model_out
                for i in range(len(q_hiddens)):
                    if use_noisy:
                        action_out = self._noisy_layer(
                            "hidden_%d" % i, action_out, q_hiddens[i], sigma0)
                    elif parameter_noise:
                        action_out = tf.keras.layers.Dense(
                            units=q_hiddens[i],
                            activation_fn=tf.nn.relu,
                            normalizer_fn=tf.keras.layers.LayerNormalization)(
                                action_out)
                    else:
                        action_out = tf.keras.layers.Dense(
                            units=q_hiddens[i],
                            activation=tf.nn.relu,
                            name="hidden_%d" % i)(action_out)
            else:
                # Avoid postprocessing the outputs. This enables custom models
                # to be used for parametric action DQN.
                action_out = model_out
            if use_noisy:
                action_scores = self._noisy_layer(
                    "output",
                    action_out,
                    self.action_space.n * num_atoms,
                    sigma0,
                    non_linear=False)
            elif q_hiddens:
                action_scores = tf.keras.layers.Dense(
                    units=self.action_space.n * num_atoms,
                    activation=None)(action_out)
            else:
                action_scores = model_out

            if num_atoms > 1:
                # Distributional Q-learning uses a discrete support z
                # to represent the action value distribution
                z = tf.range(num_atoms, dtype=tf.float32)
                z = v_min + z * (v_max - v_min) / float(num_atoms - 1)

                def _layer(x):
                    support_logits_per_action = tf.reshape(
                        tensor=x, shape=(-1, self.action_space.n, num_atoms))
                    support_prob_per_action = tf.nn.softmax(
                        logits=support_logits_per_action)
                    x = tf.reduce_sum(
                        input_tensor=z * support_prob_per_action, axis=-1)
                    logits = support_logits_per_action
                    dist = support_prob_per_action
                    return [x, z, support_logits_per_action, logits, dist]

                return tf.keras.layers.Lambda(_layer)(action_scores)
            else:
                logits = tf.expand_dims(tf.ones_like(action_scores), -1)
                dist = tf.expand_dims(tf.ones_like(action_scores), -1)
                return [action_scores, logits, dist]

        def build_state_score(model_out):
            state_out = model_out
            for i in range(len(q_hiddens)):
                if use_noisy:
                    state_out = self._noisy_layer("dueling_hidden_%d" % i,
                                                  state_out, q_hiddens[i],
                                                  sigma0)
                elif parameter_noise:
                    state_out = tf.keras.layers.Dense(
                        units=q_hiddens[i],
                        activation_fn=tf.nn.relu,
                        normalizer_fn=tf.contrib.layers.layer_norm)(state_out)
                else:
                    state_out = tf.keras.layers.Dense(
                        units=q_hiddens[i], activation=tf.nn.relu)(state_out)
            if use_noisy:
                state_score = self._noisy_layer(
                    "dueling_output",
                    state_out,
                    num_atoms,
                    sigma0,
                    non_linear=False)
            else:
                state_score = tf.keras.layers.Dense(
                    units=num_atoms, activation=None)(state_out)
            return state_score

        if tf.executing_eagerly():
            from tensorflow.python.ops import variable_scope
            # Have to use a variable store to reuse variables in eager mode
            store = variable_scope.EagerVariableStore()

            # Save the scope objects, since in eager we will execute this
            # path repeatedly and there is no guarantee it will always be run
            # in the same original scope.
            with tf.variable_scope(name + "/action_value") as action_scope:
                pass
            with tf.variable_scope(name + "/state_value") as state_scope:
                pass

            def build_action_value_in_scope(model_out):
                with store.as_default():
                    with tf.variable_scope(action_scope, reuse=tf.AUTO_REUSE):
                        return build_action_value(model_out)

            def build_state_score_in_scope(model_out):
                with store.as_default():
                    with tf.variable_scope(state_scope, reuse=tf.AUTO_REUSE):
                        return build_state_score(model_out)
        else:

            def build_action_value_in_scope(model_out):
                with tf.variable_scope(
                        name + "/action_value", reuse=tf.AUTO_REUSE):
                    return build_action_value(model_out)

            def build_state_score_in_scope(model_out):
                with tf.variable_scope(
                        name + "/state_value", reuse=tf.AUTO_REUSE):
                    return build_state_score(model_out)

        q_out = build_action_value_in_scope(self.model_out)
        self.q_value_head = tf.keras.Model(self.model_out, q_out)
        self.register_variables(self.q_value_head.variables)

        if dueling:
            state_out = build_state_score_in_scope(self.model_out)
            self.state_value_head = tf.keras.Model(self.model_out, state_out)
            self.register_variables(self.state_value_head.variables)