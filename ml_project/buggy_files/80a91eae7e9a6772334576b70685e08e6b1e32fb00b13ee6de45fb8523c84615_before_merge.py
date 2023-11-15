  def begin(self):
    var_list = tf.train.list_variables(self.checkpoint_path)

    names = []
    for name, _ in var_list:
      if (not name.startswith("optim")
          and not name.startswith("global_step")
          and not name.startswith("words_per_sec")):
        names.append(name)

    self.values = {}
    reader = tf.train.load_checkpoint(self.checkpoint_path)
    for name in names:
      self.values[name] = reader.get_tensor(name)

    tf_vars = []
    current_scope = tf.get_variable_scope()
    reuse = tf.AUTO_REUSE if hasattr(tf, "AUTO_REUSE") else True
    with tf.variable_scope(current_scope, reuse=reuse):
      for name, value in six.iteritems(self.values):
        tf_vars.append(tf.get_variable(name, shape=value.shape, dtype=tf.as_dtype(value.dtype)))

    self.placeholders = [tf.placeholder(v.dtype, shape=v.shape) for v in tf_vars]
    self.assign_ops = [tf.assign(v, p) for (v, p) in zip(tf_vars, self.placeholders)]