    def Add(self, sender, workerFn, args=(), kwargs={}, name=None, delay=0.0, uId=None, retryOnBusy=False, priority=0, workerType="dbthread"):
        """The sender will send the return value of
        workerFn(*args, **kwargs) to the main thread.
        """
        if self.utility.abcquitting:
            self._logger.debug("GUIDBHandler: abcquitting ignoring Task(%s)", name)
            return

        assert uId is None or isinstance(uId, unicode), type(uId)
        assert name is None or isinstance(name, unicode), type(name)

        if uId:
            try:
                self.uIdsLock.acquire()
                if uId in self.uIds:
                    self._logger.debug(
                        "GUIDBHandler: Task(%s) already scheduled in queue, ignoring uId = %s", name, uId)
                    return
                else:
                    self.uIds.add(uId)
            finally:
                self.uIdsLock.release()

            callbackId = uId
        else:
            callbackId = name

        self._logger.debug("GUIDBHandler: adding Task(%s)", callbackId)

        if __debug__:
            self.uIdsLock.acquire()
            self.nrCallbacks[callbackId] = self.nrCallbacks.get(callbackId, 0) + 1
            if self.nrCallbacks[callbackId] > 10:
                self._logger.debug(
                    "GUIDBHandler: Scheduled Task(%s) %d times", callbackId, self.nrCallbacks[callbackId])

            self.uIdsLock.release()

        t1 = time()

        def wrapper():
            if __debug__:
                self.uIdsLock.acquire()
                self.nrCallbacks[callbackId] = self.nrCallbacks.get(callbackId, 0) - 1
                self.uIdsLock.release()

            # Call the actual function
            try:
                t2 = time()
                result = workerFn(*args, **kwargs)

            except (AbortedException, wx.PyDeadObjectError):
                return

            except Exception as exc:
                originalTb = format_exc()
                sender.sendException(exc, originalTb)
                return

            t3 = time()
            self._logger.debug(
                "GUIDBHandler: Task(%s) took to be called %.1f (expected %.1f), actual task took %.1f %s", name, t2 - t1, delay, t3 - t2, workerType)

            if uId:
                try:
                    self.uIdsLock.acquire()
                    if uId in self.uIds:
                        self.uIds.discard(uId)

                    # this callback has been removed during wrapper, cancel now
                    else:
                        return
                finally:
                    self.uIdsLock.release()

            # if we get to this step, send result to callback
            try:
                sender.sendResult(result)
            except:
                print_exc()
                self._logger.error("GUIDBHandler: Could not send result of Task(%s)", name)

        wrapper.__name__ = str(name)

        # Have in mind that setting workerType to "ThreadPool" means that the
        # task wants to be executed OUT of the GUI thread, nothing more.
        if delay or not (isInIOThread() or isInThreadPool()):
            if workerType == "dbThread":
                # Schedule the task to be called later in the reactor thread.
                self.utility.session.lm.threadpool.add_task(wrapper, delay)
            elif workerType == "ThreadPool":
                self.utility.session.lm.threadpool.add_task_in_thread(wrapper, delay)
            else:
                raise RuntimeError("Asked to schedule a task with unknown workerType: %s", workerType)
        elif workerType == "dbThread" and not isInIOThread():
            reactor.callFromThread(wrapper)
        else:
            self._logger.debug("GUIDBHandler: Task(%s) scheduled to be called on non GUI thread from non GUI thread, "
                               "executing synchronously.", name)
            wrapper()