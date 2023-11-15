    def _init_command_dispatcher(self):
        dispatcher = commands.CommandDispatcher(self.win_id,
                                                self.tabbed_browser)
        objreg.register('command-dispatcher', dispatcher, scope='window',
                        window=self.win_id)
        self.tabbed_browser.destroyed.connect(
            functools.partial(objreg.delete, 'command-dispatcher',
                              scope='window', window=self.win_id))