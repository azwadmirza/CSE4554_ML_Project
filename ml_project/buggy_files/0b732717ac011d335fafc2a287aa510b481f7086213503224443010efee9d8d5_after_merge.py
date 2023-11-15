    def _noisy_layer(self,
                     prefix,
                     action_in,
                     out_size,
                     sigma0,
                     non_linear=True):
        """
        a common dense layer: y = w^{T}x + b
        a noisy layer: y = (w + \\epsilon_w*\\sigma_w)^{T}x +
            (b+\\epsilon_b*\\sigma_b)
        where \epsilon are random variables sampled from factorized normal
        distributions and \\sigma are trainable variables which are expected to
        vanish along the training procedure
        """
        in_size = int(action_in.shape[1])

        epsilon_in = tf.random_normal(shape=[in_size])
        epsilon_out = tf.random_normal(shape=[out_size])
        epsilon_in = self._f_epsilon(epsilon_in)
        epsilon_out = self._f_epsilon(epsilon_out)
        epsilon_w = tf.matmul(
            a=tf.expand_dims(epsilon_in, -1), b=tf.expand_dims(epsilon_out, 0))
        epsilon_b = epsilon_out
        sigma_w = tf.get_variable(
            name=prefix + "_sigma_w",
            shape=[in_size, out_size],
            dtype=tf.float32,
            initializer=tf.random_uniform_initializer(
                minval=-1.0 / np.sqrt(float(in_size)),
                maxval=1.0 / np.sqrt(float(in_size))))
        # TF noise generation can be unreliable on GPU
        # If generating the noise on the CPU,
        # lowering sigma0 to 0.1 may be helpful
        sigma_b = tf.get_variable(
            name=prefix + "_sigma_b",
            shape=[out_size],
            dtype=tf.float32,  # 0.5~GPU, 0.1~CPU
            initializer=tf.constant_initializer(
                sigma0 / np.sqrt(float(in_size))))

        w = tf.get_variable(
            name=prefix + "_fc_w",
            shape=[in_size, out_size],
            dtype=tf.float32,
            initializer=tf.initializers.glorot_uniform())
        b = tf.get_variable(
            name=prefix + "_fc_b",
            shape=[out_size],
            dtype=tf.float32,
            initializer=tf.zeros_initializer())

        action_activation = \
            tf.keras.layers.Lambda(lambda x: tf.matmul(
                x, w + sigma_w * epsilon_w) + b + sigma_b * epsilon_b)(
                action_in)

        if not non_linear:
            return action_activation
        return tf.nn.relu(action_activation)