    def _one_step_forward_per_replica(self, batch):
        if self.config["gradient_accumulation_steps"] == 1:
            gradients, per_replica_losses = self._calculate_gradient_per_batch(batch)
            self._optimizer.apply_gradients(
                zip(gradients, self._trainable_variables), 1.0
            )
        else:
            # gradient acummulation here.
            per_replica_losses = 0.0
            for i in tf.range(self.config["gradient_accumulation_steps"]):
                reduced_batch = {
                    k: v[
                        i
                        * self.config["batch_size"] : (i + 1)
                        * self.config["batch_size"]
                    ]
                    for k, v in batch.items()
                }

                # run 1 step accumulate
                reduced_batch_losses = self._calculate_gradient_per_batch(reduced_batch)

                # sum per_replica_losses
                per_replica_losses += reduced_batch_losses

            gradients = self._gradient_accumulator.gradients
            self._optimizer.apply_gradients(
                zip(gradients, self._trainable_variables), 1.0
            )
            self._gradient_accumulator.reset()

        return per_replica_losses