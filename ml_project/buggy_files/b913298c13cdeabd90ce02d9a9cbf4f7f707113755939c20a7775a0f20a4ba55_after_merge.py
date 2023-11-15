    def _home(self):
        if self._home_cached is not None:
            return self._home_cached
        for _ in range(MAX_HOME_RETRIES - 1):
            try:
                self._home_cached = self._try_to_get_home()
                return self._home_cached
            except Exception:
                # TODO (Dmitri): Identify the exception we're trying to avoid.
                logger.info("Error reading container's home directory. "
                            f"Retrying in {HOME_RETRY_DELAY_S} seconds.")
                time.sleep(HOME_RETRY_DELAY_S)
        # Last try
        self._home_cached = self._try_to_get_home()
        return self._home_cached