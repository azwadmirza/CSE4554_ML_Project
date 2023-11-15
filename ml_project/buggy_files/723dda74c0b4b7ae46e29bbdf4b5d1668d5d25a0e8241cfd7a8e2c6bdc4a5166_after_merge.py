    def __init__(self, runtime_configuration, bot_id, run_subcommand=None, console_type=None,
                 message_kind=None, dryrun=None, msg=None, show=None, loglevel=None):
        self.runtime_configuration = runtime_configuration
        module = import_module(self.runtime_configuration['module'])

        if loglevel:
            self.leverageLogger(loglevel)
        elif run_subcommand == "console":
            self.leverageLogger("DEBUG")

        bot = getattr(module, 'BOT')
        if run_subcommand == "message":
            bot.init = lambda *args, **kwargs: None
        self.instance = bot(bot_id, disable_multithreading=True)

        if not run_subcommand:
            self.instance.start()
        else:
            self.instance._Bot__connect_pipelines()
            if run_subcommand == "console":
                self._console(console_type)
            elif run_subcommand == "message":
                self._message(message_kind, msg)
                return
            elif run_subcommand == "process":
                self._process(dryrun, msg, show)
            else:
                print("Subcommand {} not known.".format(run_subcommand))