    def Remove(self, uId):
        if uId in self.uIds:
            self._logger.debug("GUIDBHandler: removing Task(%s)", uId)

            with self.uIdsLock:
                self.uIds.discard(uId)

                if __debug__:
                    self.nrCallbacks[uId] = self.nrCallbacks.get(uId, 0) - 1

            self.utility.session.lm.threadpool.cancel_pending_task(uId)