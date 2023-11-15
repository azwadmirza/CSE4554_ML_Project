    def _gather_rollout(self, rollout_number, last_observation):
        assert 0 < self._path_lengths[
            rollout_number] <= self._max_episode_length
        traj = TrajectoryBatch(
            env_spec=self._envs[rollout_number].spec,
            observations=np.asarray(self._observations[rollout_number]),
            last_observations=np.asarray([last_observation]),
            actions=np.asarray(self._actions[rollout_number]),
            rewards=np.asarray(self._rewards[rollout_number]),
            step_types=np.asarray(self._step_types[rollout_number],
                                  dtype=StepType),
            env_infos=self._env_infos[rollout_number],
            agent_infos=self._agent_infos[rollout_number],
            lengths=np.asarray([self._path_lengths[rollout_number]],
                               dtype='l'))
        self._completed_rollouts.append(traj)
        self._observations[rollout_number] = []
        self._actions[rollout_number] = []
        self._rewards[rollout_number] = []
        self._step_types[rollout_number] = []
        self._path_lengths[rollout_number] = 0
        self._prev_obs[rollout_number] = self._envs[rollout_number].reset()