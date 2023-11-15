  def begin(self):
    names = set()
    for name, _ in tf.train.list_variables(self.checkpoint_path):
      if (not name.startswith("optim")
          and not name.startswith("global_step")
          and not name.startswith("words_per_sec")):
        names.add(name)

    reader = tf.train.load_checkpoint(self.checkpoint_path)
    variables = tf.trainable_variables()
    for variable in variables:
      name = variable.op.name
      if name in names:
        value = reader.get_tensor(name)
        self.assign_pairs.append((variable, value))