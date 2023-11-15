    def __report_error(self, exc_info):
        if isinstance(exc_info[1], GreenletExit):
            self.__report_result(exc_info[1])
            return

        self._exc_info = exc_info[0], exc_info[1], dump_traceback(exc_info[2])

        hub = get_my_hub(self) # pylint:disable=undefined-variable
        if self._links and not self._notifier:
            self._notifier = hub.loop.run_callback(self._notify_links)

        try:
            hub.handle_error(self, *exc_info)
        finally:
            del exc_info