    def commit_now(self, vacuum=False, exiting=False):
        if self._should_commit and isInIOThread():
            try:
                self._logger.info(u"Start committing...")
                self.execute(u"COMMIT;")
            except:
                self._logger.exception(u"COMMIT FAILED")
                if exiting:
                    # If we are exiting we don't propagate the error.
                    # The reason for the exit may be the reason this exception occurred.
                    self._logger.exception(u"Not propagating commit error, as we are exiting")
                    return
                else:
                    raise
            self._should_commit = False

            if vacuum:
                self._logger.info(u"Start vacuuming...")
                self.execute(u"VACUUM;")

            if not exiting:
                try:
                    self._logger.info(u"Beginning another transaction...")
                    self.execute(u"BEGIN;")
                except:
                    self._logger.exception(u"Failed to execute BEGIN")
                    raise
            else:
                self._logger.info(u"Exiting, not beginning another transaction")

        elif vacuum:
            self.execute(u"VACUUM;")