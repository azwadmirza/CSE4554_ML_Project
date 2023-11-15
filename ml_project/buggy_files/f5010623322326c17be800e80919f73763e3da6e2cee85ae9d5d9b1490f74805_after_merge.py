    def keep_learning_about_nodes(self):
        """
        Continually learn about new nodes.
        """

        # TODO: Allow the user to set eagerness?  1712
        # TODO: Also, if we do allow eager, don't even defer; block right here.

        self._learning_deferred = Deferred(canceller=self._discovery_canceller)  # TODO: No longer relevant.

        def _discover_or_abort(_first_result):
            # self.log.debug(f"{self} learning at {datetime.datetime.now()}")   # 1712
            result = self.learn_from_teacher_node(eager=False, canceller=self._discovery_canceller)
            # self.log.debug(f"{self} finished learning at {datetime.datetime.now()}")  # 1712
            return result

        self._learning_deferred.addCallback(_discover_or_abort)
        self._learning_deferred.addErrback(self.handle_learning_errors)

        # Instead of None, we might want to pass something useful about the context.
        # Alternately, it might be nice for learn_from_teacher_node to (some or all of the time) return a Deferred.
        reactor.callInThread(self._learning_deferred.callback, None)
        return self._learning_deferred