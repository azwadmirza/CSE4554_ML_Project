    def learn_on_batch(self, samples: SampleBatchType) -> dict:
        """Update policies based on the given batch.

        This is the equivalent to apply_gradients(compute_gradients(samples)),
        but can be optimized to avoid pulling gradients into CPU memory.

        Returns:
            info: dictionary of extra metadata from compute_gradients().

        Examples:
            >>> batch = worker.sample()
            >>> worker.learn_on_batch(samples)
        """
        if log_once("learn_on_batch"):
            logger.info(
                "Training on concatenated sample batches:\n\n{}\n".format(
                    summarize(samples)))
        if isinstance(samples, MultiAgentBatch):
            info_out = {}
            to_fetch = {}
            if self.tf_sess is not None:
                builder = TFRunBuilder(self.tf_sess, "learn_on_batch")
            else:
                builder = None
            for pid, batch in samples.policy_batches.items():
                if pid not in self.policies_to_train:
                    continue
                policy = self.policy_map[pid]
                if builder and hasattr(policy, "_build_learn_on_batch"):
                    to_fetch[pid] = policy._build_learn_on_batch(
                        builder, batch)
                else:
                    info_out[pid] = policy.learn_on_batch(batch)
            info_out.update({k: builder.get(v) for k, v in to_fetch.items()})
        else:
            info_out = {
                DEFAULT_POLICY_ID: self.policy_map[DEFAULT_POLICY_ID]
                .learn_on_batch(samples)
            }
        if log_once("learn_out"):
            logger.debug("Training out:\n\n{}\n".format(summarize(info_out)))
        return info_out