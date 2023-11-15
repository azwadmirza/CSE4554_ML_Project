    def unhandled_error_observer(self, loop, context):
        """
        This method is called when an unhandled error in Tribler is observed.
        It broadcasts the tribler_exception event.
        """
        try:
            exception = context.get('exception')
            ignored_message = None
            try:
                ignored_message = IGNORED_ERRORS.get(
                    (exception.__class__, exception.errno),
                    IGNORED_ERRORS.get(exception.__class__))
            except (ValueError, AttributeError):
                pass
            if ignored_message is not None:
                self._logger.error(ignored_message if ignored_message != "" else context.get('message'))
                return

            text = str(exception or context.get('message'))

            # We already have a check for invalid infohash when adding a torrent, but if somehow we get this
            # error then we simply log and ignore it.
            if isinstance(exception, RuntimeError) and 'invalid info-hash' in text:
                self._logger.error("Invalid info-hash found")
                return

            text_long = text
            exc = context.get('exception')
            if exc:
                with StringIO() as buffer:
                    print_exception(type(exc), exc, exc.__traceback__, file=buffer)
                    text_long = text_long + "\n--LONG TEXT--\n" + buffer.getvalue()
            text_long = text_long + "\n--CONTEXT--\n" + str(context)

            description = 'session.unhandled_error_observer()'
            with AllowSentryReports(value=False, description=description):
                self._logger.error("Unhandled exception occurred! %s", text_long)
            sentry_event = SentryReporter.last_event

            if not self.api_manager:
                return

            events = self.api_manager.get_endpoint('events')
            events.on_tribler_exception(text_long, sentry_event)

            state = self.api_manager.get_endpoint('state')
            state.on_tribler_exception(text_long, sentry_event)
        except Exception as e:
            SentryReporter.send_exception_with_confirmation(e)
            raise e