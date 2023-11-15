    def compute_nstep_return(
        batch: Batch,
        buffer: ReplayBuffer,
        indice: np.ndarray,
        target_q_fn: Callable[[ReplayBuffer, np.ndarray], torch.Tensor],
        gamma: float = 0.99,
        n_step: int = 1,
        rew_norm: bool = False,
    ) -> Batch:
        r"""Compute n-step return for Q-learning targets.

        .. math::
            G_t = \sum_{i = t}^{t + n - 1} \gamma^{i - t}(1 - d_i)r_i +
            \gamma^n (1 - d_{t + n}) Q_{\mathrm{target}}(s_{t + n})

        where :math:`\gamma` is the discount factor,
        :math:`\gamma \in [0, 1]`, :math:`d_t` is the done flag of step
        :math:`t`.

        :param batch: a data batch, which is equal to buffer[indice].
        :type batch: :class:`~tianshou.data.Batch`
        :param buffer: a data buffer which contains several full-episode data
            chronologically.
        :type buffer: :class:`~tianshou.data.ReplayBuffer`
        :param indice: sampled timestep.
        :type indice: numpy.ndarray
        :param function target_q_fn: a function receives :math:`t+n-1` step's
            data and compute target Q value.
        :param float gamma: the discount factor, should be in [0, 1], defaults
            to 0.99.
        :param int n_step: the number of estimation step, should be an int
            greater than 0, defaults to 1.
        :param bool rew_norm: normalize the reward to Normal(0, 1), defaults
            to False.

        :return: a Batch. The result will be stored in batch.returns as a
            torch.Tensor with shape (bsz, ).
        """
        rew = buffer.rew
        if rew_norm:
            bfr = rew[:min(len(buffer), 1000)]  # avoid large buffer
            mean, std = bfr.mean(), bfr.std()
            if np.isclose(std, 0, 1e-2):
                mean, std = 0.0, 1.0
        else:
            mean, std = 0.0, 1.0
        buf_len = len(buffer)
        terminal = (indice + n_step - 1) % buf_len
        target_q_torch = target_q_fn(buffer, terminal).flatten()  # (bsz, )
        target_q = to_numpy(target_q_torch)

        target_q = _nstep_return(rew, buffer.done, target_q, indice,
                                 gamma, n_step, len(buffer), mean, std)

        batch.returns = to_torch_as(target_q, target_q_torch)
        # prio buffer update
        if isinstance(buffer, PrioritizedReplayBuffer):
            batch.weight = to_torch_as(batch.weight, target_q_torch)
        return batch