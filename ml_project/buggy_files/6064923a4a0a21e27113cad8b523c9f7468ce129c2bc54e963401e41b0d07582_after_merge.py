    def _log_sync_progress(
        self, polled_block_number: BlockNumber, target_block: BlockNumber
    ) -> None:
        """Print a message if there are many blocks to be fetched, or if the
        time in-between polls is high.
        """
        now = time.monotonic()
        blocks_until_target = target_block - polled_block_number
        polled_block_count = polled_block_number - self.last_log_block
        elapsed = now - self.last_log_time

        if blocks_until_target > 100 or elapsed > 15.0:
            log.info(
                "Synchronizing blockchain events",
                remaining_blocks_to_sync=blocks_until_target,
                blocks_per_second=polled_block_count / elapsed,
                to_block=target_block,
                elapsed=elapsed,
            )
            self.last_log_time = time.monotonic()
            self.last_log_block = polled_block_number