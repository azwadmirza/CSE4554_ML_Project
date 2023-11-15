    def __init__(self, bot_id: str, start=False, sighup_event=None,
                 disable_multithreading=None):
        super().__init__(bot_id=bot_id)
        if self.__class__.__name__ == 'ParserBot':
            self.logger.error('ParserBot can\'t be started itself. '
                              'Possible Misconfiguration.')
            self.stop()
        self.group = 'Parser'