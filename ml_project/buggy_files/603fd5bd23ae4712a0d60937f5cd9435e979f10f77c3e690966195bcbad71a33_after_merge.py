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