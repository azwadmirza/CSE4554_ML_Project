    def bot_run(self, bot_id):
        try:
            bot_module = self.startup[bot_id]['module']
        except KeyError:
            log_bot_error('notfound', bot_id)
            return 'error'
        else:
            module = importlib.import_module(bot_module)
            # TODO: Search for bot class is dirty (but works)
            botname = [name for name in dir(module)
                       if hasattr(getattr(module, name), 'process') and
                       name.endswith('Bot') and
                       name != 'ParserBot'][0]
            bot = getattr(module, botname)
            instance = bot(bot_id)
            instance.start()