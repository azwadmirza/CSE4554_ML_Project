    def _pooled(self):
        thr_name = current_thread().getName()
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug("Closing run_async thread %s/%d", thr_name,
                                  len(self.__async_threads))
                break

            promise.run()

            if not promise.exception:
                self.update_persistence(update=promise.update)
                continue

            if isinstance(promise.exception, DispatcherHandlerStop):
                self.logger.warning(
                    'DispatcherHandlerStop is not supported with async functions; func: %s',
                    promise.pooled_function.__name__)
                continue

            # Avoid infinite recursion of error handlers.
            if promise.pooled_function in self.error_handlers:
                self.logger.error('An uncaught error was raised while handling the error.')
                continue

            # Don't perform error handling for a `Promise` with deactivated error handling. This
            # should happen only via the deprecated `@run_async` decorator or `Promises` created
            # within error handlers
            if not promise.error_handling:
                self.logger.error('A promise with deactivated error handling raised an error.')
                continue

            # If we arrive here, an exception happened in the promise and was neither
            # DispatcherHandlerStop nor raised by an error handler. So we can and must handle it
            try:
                self.dispatch_error(promise.update, promise.exception, promise=promise)
            except Exception:
                self.logger.exception('An uncaught error was raised while handling the error.')