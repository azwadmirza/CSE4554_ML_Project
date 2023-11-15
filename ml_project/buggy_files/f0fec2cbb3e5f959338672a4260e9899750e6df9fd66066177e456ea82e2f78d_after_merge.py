    def kill(self):
        # type: () -> None
        """Terminates the job if it is still running.

        N.B.: This method is idempotent.
        """
        try:
            self._process.kill()
        except OSError as e:
            if e.errno != errno.ESRCH:
                raise e
        finally:
            self._finalize_job()