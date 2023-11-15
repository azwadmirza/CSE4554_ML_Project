    def on_checkpoint(self, checkpoint):
        """Starts tracking checkpoint metadata on checkpoint.

        Sets the newest checkpoint. For PERSISTENT checkpoints: Deletes
        previous checkpoint as long as it isn't one of the best ones. Also
        deletes the worst checkpoint if at capacity.

        Args:
            checkpoint (Checkpoint): Trial state checkpoint.
        """
        if checkpoint.storage == Checkpoint.MEMORY:
            self.newest_memory_checkpoint = checkpoint
            return

        old_checkpoint = self.newest_persistent_checkpoint

        if old_checkpoint.value == checkpoint.value:
            return

        self.newest_persistent_checkpoint = checkpoint

        # Remove the old checkpoint if it isn't one of the best ones.
        if old_checkpoint.value and old_checkpoint not in self._membership:
            self.delete(old_checkpoint)

        try:
            queue_item = QueueItem(self._priority(checkpoint), checkpoint)
        except KeyError:
            logger.error("Result dict has no key: {}. "
                         "checkpoint_score_attr must be set to a key in the "
                         "result dict.".format(self._checkpoint_score_attr))
            return

        if len(self._best_checkpoints) < self.keep_checkpoints_num:
            heapq.heappush(self._best_checkpoints, queue_item)
            self._membership.add(checkpoint)
        elif queue_item.priority >= self._best_checkpoints[0].priority:
            worst = heapq.heappushpop(self._best_checkpoints, queue_item).value
            self._membership.add(checkpoint)
            if worst in self._membership:
                self._membership.remove(worst)
            # Don't delete the newest checkpoint. It will be deleted on the
            # next on_checkpoint() call since it isn't in self._membership.
            if worst != checkpoint:
                self.delete(worst)