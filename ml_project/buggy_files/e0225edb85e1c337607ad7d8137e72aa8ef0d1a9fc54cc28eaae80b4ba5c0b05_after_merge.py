    def local_train(self, file_list, batch_size, epoch=1, kwargs=None):
        """
        Local training for local testing. Must in eager mode.
        Argments:
            batch_size: batch size in training
            epoch: the number of epoch in training
            kwargs: contains a dict of parameters used in training
        """
        optimizer = self._opt_fn()
        for _ in range(epoch):
            for f in file_list:
                with recordio.File(f, "r", decoder=self._codec.decode) as rdio_r:
                    reader = rdio_r.get_reader(0, rdio_r.count())
                    while True:
                        record_buf = list(
                            itertools.islice(reader, 0, batch_size))
                        if not record_buf:
                            break

                        data, labels = self._input_fn(record_buf)

                        with tf.GradientTape() as tape:
                            inputs = []
                            for f_col in self._feature_columns:
                                inputs.append(data[f_col.key])
                            if len(inputs) == 1:
                                inputs = inputs[0]
                            outputs = self._model.call(inputs, training=True)
                            loss = self._loss(outputs, labels)

                            # Add regularization loss if any.
                            # Note: for distributed training, the regularization loss should
                            #       be divided by the number of contributing workers, which
                            #       might be difficult for elasticdl.
                            if self._model.losses:
                                loss += math_ops.add_n(self._model.losses)
                        grads = tape.gradient(
                            loss, self._model.trainable_variables)
                        optimizer.apply_gradients(
                            zip(grads, self._model.trainable_variables))
                        print("Loss is ", loss.numpy())