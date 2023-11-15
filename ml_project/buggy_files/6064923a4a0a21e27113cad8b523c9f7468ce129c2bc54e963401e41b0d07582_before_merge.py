    def _log_sync_progress(self, to_block: BlockNumber) -> None:
        """Print a message if there are many blocks to be fetched, or if the
        time in-between polls is high.
        """
        now = datetime.now()
        blocks_to_sync = to_block - self.last_log_block
        elapsed = (now - self.last_log_time).total_seconds()

        if blocks_to_sync > 100 or elapsed > 15.0:
            log.info(
                "Synchronizing blockchain events",
                blocks_to_sync=blocks_to_sync,
                blocks_per_second=blocks_to_sync / elapsed,
                to_block=to_block,
                elapsed=elapsed,
            )
            self.last_log_time = now

        self.last_log_block = to_block