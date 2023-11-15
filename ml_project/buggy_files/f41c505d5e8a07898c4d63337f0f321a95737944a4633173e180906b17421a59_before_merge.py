    def __init__(self,
                 c_path=os.path.join(syspaths.CONFIG_DIR, 'master'),
                 mopts=None, skip_perm_errors=False,
                 io_loop=None, keep_loop=False, auto_reconnect=False):
        '''
        :param IOLoop io_loop: io_loop used for events.
                               Pass in an io_loop if you want asynchronous
                               operation for obtaining events. Eg use of
                               set_event_handler() API. Otherwise,
                               operation will be synchronous.
        '''
        if mopts:
            self.opts = mopts
        else:
            if os.path.isdir(c_path):
                log.warning(
                    '{0} expects a file path not a directory path({1}) to '
                    'it\'s \'c_path\' keyword argument'.format(
                        self.__class__.__name__, c_path
                    )
                )
            self.opts = salt.config.client_config(c_path)
        self.serial = salt.payload.Serial(self.opts)
        self.salt_user = salt.utils.get_specific_user()
        self.skip_perm_errors = skip_perm_errors
        self.key = self.__read_master_key()
        self.auto_reconnect = auto_reconnect
        self.event = salt.utils.event.get_event(
                'master',
                self.opts['sock_dir'],
                self.opts['transport'],
                opts=self.opts,
                listen=False,
                io_loop=io_loop,
                keep_loop=keep_loop,
                raise_errors=auto_reconnect)
        self.utils = salt.loader.utils(self.opts)
        self.functions = salt.loader.minion_mods(self.opts, utils=self.utils)
        self.returners = salt.loader.returners(self.opts, self.functions)