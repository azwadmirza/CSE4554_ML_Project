    def __init__(self, args=None, config=None):
        """Init the plugin."""
        super(Plugin, self).__init__(args=args,
                                     config=config,
                                     stats_init_value=[])

        # We want to display the stat in the curse interface
        self.display_curse = True

        # Trying to display proc time
        self.tag_proc_time = True

        # Call CorePlugin to get the core number (needed when not in IRIX mode / Solaris mode)
        try:
            self.nb_log_core = CorePlugin(args=self.args).update()["log"]
        except Exception:
            self.nb_log_core = 0

        # Get the max values (dict)
        self.max_values = copy.deepcopy(glances_processes.max_values())

        # Get the maximum PID number
        # Use to optimize space (see https://github.com/nicolargo/glances/issues/959)
        self.pid_max = glances_processes.pid_max

        # Set the default sort key if it is defined in the configuration file
        if 'processlist' in config.as_dict() and 'sort_key' in config.as_dict()['processlist']:
            logger.debug('Configuration overwrites processes sort key by {}'.format(config.as_dict()['processlist']['sort_key']))
            glances_processes.set_sort_key(config.as_dict()['processlist']['sort_key'], False)