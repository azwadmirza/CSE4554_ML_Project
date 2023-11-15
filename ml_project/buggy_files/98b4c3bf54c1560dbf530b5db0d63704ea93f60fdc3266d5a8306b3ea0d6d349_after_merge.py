    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        global DONT_COLORIZE
        DONT_COLORIZE = self._plugin_options['nocolor']