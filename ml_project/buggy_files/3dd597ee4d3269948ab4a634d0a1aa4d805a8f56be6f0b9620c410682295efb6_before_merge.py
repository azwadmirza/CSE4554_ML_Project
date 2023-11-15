    def post_process_fn(
        self, batch: Batch, buffer: ReplayBuffer, indice: np.ndarray
    ) -> None:
        """Post-process the data from the provided replay buffer.

        Typical usage is to update the sampling weight in prioritized
        experience replay. Used in :meth:`update`.
        """
        if isinstance(buffer, PrioritizedReplayBuffer) and hasattr(
            batch, "weight"
        ):
            buffer.update_weight(indice, batch.weight)