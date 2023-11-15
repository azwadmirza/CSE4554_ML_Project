    def distributed_train(self):
        """
        Distributed training.
        """
        while True:
            task = self.get_task()
            if not task.shard_file_name:
                # No more task
                break
            batch_size = task.minibatch_size
            err_msg = ""
            try:
                with recordio.File(task.shard_file_name, "r", decoder=self._codec.decode) as rdio_r:
                    reader = rdio_r.get_reader(task.start, task.end)
                    min_model_version = task.model_version
                    while True:
                        record_buf = list(
                            itertools.islice(reader, 0, batch_size))
                        if not record_buf:
                            break

                        for _ in range(self._max_retrain_num):
                            # TODO: optimize the logic to avoid unnecessary get_model call.
                            self.get_model(
                                max(self._model_version, min_model_version))

                            batch_input_data, batch_label = self._input_fn(record_buf)

                            with tf.GradientTape() as tape:
                                inputs = []
                                for f_col in self._feature_columns:
                                    inputs.append(batch_input_data[f_col.key])
                                if len(inputs) == 1:
                                    inputs = inputs[0]
                                outputs = self._model.call(inputs, training=True)
                                loss = self._loss(outputs, batch_label.flatten())

                                # TODO:  Add regularization loss if any,
                                #        which should be divided by the number of contributing workers.
                            grads = tape.gradient(
                                loss, self._model.trainable_variables)
                            print("Loss is ", loss.numpy())

                            accepted, min_model_version = self.report_gradient(
                                grads)
                            if accepted:
                                break
                        else:
                            # Worker got stuck, fail the task.
                            # TODO: stop the worker if it fails to make any progress for some time.
                            raise RuntimeError("Worker got stuck")


            except Exception as ex:
                err_msg = str(ex)
                traceback.print_exc()
            self.report_task_result(task.task_id, err_msg)