    def action_prob(self, batch: SampleBatchType) -> np.ndarray:
        """Returns the probs for the batch actions for the current policy."""

        num_state_inputs = 0
        for k in batch.keys():
            if k.startswith("state_in_"):
                num_state_inputs += 1
        state_keys = ["state_in_{}".format(i) for i in range(num_state_inputs)]
        log_likelihoods: TensorType = self.policy.compute_log_likelihoods(
            actions=batch[SampleBatch.ACTIONS],
            obs_batch=batch[SampleBatch.CUR_OBS],
            state_batches=[batch[k] for k in state_keys],
            prev_action_batch=batch.data.get(SampleBatch.PREV_ACTIONS),
            prev_reward_batch=batch.data.get(SampleBatch.PREV_REWARDS))
        return convert_to_numpy(log_likelihoods)