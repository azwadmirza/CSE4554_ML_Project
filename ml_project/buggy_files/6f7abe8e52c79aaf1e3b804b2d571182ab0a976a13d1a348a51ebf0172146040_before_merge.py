    def __init__(self, dispatcher):
        """
        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`):
        """
        if not dispatcher.use_context:
            raise ValueError('CallbackContext should not be used with a non context aware '
                             'dispatcher!')
        self._dispatcher = dispatcher
        self._bot_data = dispatcher.bot_data
        self._chat_data = None
        self._user_data = None
        self.args = None
        self.matches = None
        self.error = None
        self.job = None