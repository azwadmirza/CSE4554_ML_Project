    def _train(self):
        config = self.config

        step_tstart = time.time()
        theta = self.policy.get_weights()
        assert theta.dtype == np.float32

        # Put the current policy weights in the object store.
        theta_id = ray.put(theta)
        # Use the actors to do rollouts, note that we pass in the ID of the
        # policy weights.
        results, num_episodes, num_timesteps = self._collect_results(
            theta_id,
            config["episodes_per_batch"],
            config["timesteps_per_batch"])

        all_noise_indices = []
        all_training_returns = []
        all_training_lengths = []
        all_eval_returns = []
        all_eval_lengths = []

        # Loop over the results.
        for result in results:
            all_eval_returns += result.eval_returns
            all_eval_lengths += result.eval_lengths

            all_noise_indices += result.noise_indices
            all_training_returns += result.noisy_returns
            all_training_lengths += result.noisy_lengths

        assert len(all_eval_returns) == len(all_eval_lengths)
        assert (len(all_noise_indices) == len(all_training_returns) ==
                len(all_training_lengths))

        self.episodes_so_far += num_episodes
        self.timesteps_so_far += num_timesteps

        # Assemble the results.
        eval_returns = np.array(all_eval_returns)
        eval_lengths = np.array(all_eval_lengths)
        noise_indices = np.array(all_noise_indices)
        noisy_returns = np.array(all_training_returns)
        noisy_lengths = np.array(all_training_lengths)

        # Process the returns.
        if config["return_proc_mode"] == "centered_rank":
            proc_noisy_returns = utils.compute_centered_ranks(noisy_returns)
        else:
            raise NotImplementedError(config["return_proc_mode"])

        # Compute and take a step.
        g, count = utils.batched_weighted_sum(
            proc_noisy_returns[:, 0] - proc_noisy_returns[:, 1],
            (self.noise.get(index, self.policy.num_params)
             for index in noise_indices),
            batch_size=500)
        g /= noisy_returns.size
        assert (
            g.shape == (self.policy.num_params,) and
            g.dtype == np.float32 and
            count == len(noise_indices))
        # Compute the new weights theta.
        theta, update_ratio = self.optimizer.update(
            -g + config["l2_coeff"] * theta)
        # Set the new weights in the local copy of the policy.
        self.policy.set_weights(theta)

        step_tend = time.time()
        tlogger.record_tabular("EvalEpRewMean", eval_returns.mean())
        tlogger.record_tabular("EvalEpRewStd", eval_returns.std())
        tlogger.record_tabular("EvalEpLenMean", eval_lengths.mean())

        tlogger.record_tabular("EpRewMean", noisy_returns.mean())
        tlogger.record_tabular("EpRewStd", noisy_returns.std())
        tlogger.record_tabular("EpLenMean", noisy_lengths.mean())

        tlogger.record_tabular("Norm", float(np.square(theta).sum()))
        tlogger.record_tabular("GradNorm", float(np.square(g).sum()))
        tlogger.record_tabular("UpdateRatio", float(update_ratio))

        tlogger.record_tabular("EpisodesThisIter", noisy_lengths.size)
        tlogger.record_tabular("EpisodesSoFar", self.episodes_so_far)
        tlogger.record_tabular("TimestepsThisIter", noisy_lengths.sum())
        tlogger.record_tabular("TimestepsSoFar", self.timesteps_so_far)

        tlogger.record_tabular("TimeElapsedThisIter", step_tend - step_tstart)
        tlogger.record_tabular("TimeElapsed", step_tend - self.tstart)
        tlogger.dump_tabular()

        info = {
            "weights_norm": np.square(theta).sum(),
            "grad_norm": np.square(g).sum(),
            "update_ratio": update_ratio,
            "episodes_this_iter": noisy_lengths.size,
            "episodes_so_far": self.episodes_so_far,
            "timesteps_this_iter": noisy_lengths.sum(),
            "timesteps_so_far": self.timesteps_so_far,
            "time_elapsed_this_iter": step_tend - step_tstart,
            "time_elapsed": step_tend - self.tstart
        }

        result = TrainingResult(
            episode_reward_mean=eval_returns.mean(),
            episode_len_mean=eval_lengths.mean(),
            timesteps_this_iter=noisy_lengths.sum(),
            info=info)

        return result