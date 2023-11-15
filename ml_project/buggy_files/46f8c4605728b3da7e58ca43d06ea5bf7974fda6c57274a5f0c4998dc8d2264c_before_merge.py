    def _assign_uwsgi_mule_message_handler(self, obj, method, configured, message_callback=None, flush=True, **kwargs):
        """Assign object to a handler by sending a setup message to the appropriate handler pool (farm), where a handler
        (mule) will receive the message and assign itself.

        :param obj:             Same as :method:`ConfiguresHandlers.assign_handler()`.
        :param method:          Same as :method:`ConfiguresHandlers._assign_db_preassign_handler()`.
        :param configured:      Same as :method:`ConfiguresHandlers.assign_handler()`.
        :param queue_callback:  Callback returning a setup message to be sent via the stack messaging interface's
                                ``send_message()`` method. No arguments are passed.
        :type queue_callback:   callable

        :raises HandlerAssignmentSkip: if the configured or default handler is not a known handler pool (farm)
        :returns: str -- The assigned handler pool.
        """
        assert message_callback is not None, \
            "Cannot perform '%s' handler assignment: `message_callback` is None" \
            % HANDLER_ASSIGNMENT_METHODS.UWSGI_MULE_MESSAGE
        tag = configured or self.DEFAULT_HANDLER_TAG
        pool = self.pool_for_tag.get(tag)
        if pool is None:
            log.debug("(%s) No handler pool (uWSGI farm) for '%s' found", obj.log_str(), tag)
            raise HandlerAssignmentSkip()
        else:
            if flush:
                _timed_flush_obj(obj)
            message = message_callback()
            self.app.application_stack.send_message(pool, message)
        return pool