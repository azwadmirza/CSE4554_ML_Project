    def __init__(self, kernel_manager, connection_file_mode, **kw):
        self.kernel_manager = kernel_manager
        # use the zero-ip from the start, can prevent having to write out connection file again
        self.kernel_manager.ip = '0.0.0.0'

        self.connection_file_mode = connection_file_mode
        if self.connection_file_mode:
            if self.connection_file_mode not in connection_file_modes:
                self.log.warning("Unknown connection file mode detected '{}'!  Continuing...".
                                 format(self.connection_file_mode))

        self.log = kernel_manager.log
        # extract the kernel_id string from the connection file and set the KERNEL_ID environment variable
        self.kernel_id = os.path.basename(self.kernel_manager.connection_file). \
            replace('kernel-', '').replace('.json', '')

        # ask the subclass for the set of applicable hosts
        self.hosts = self.get_hosts()

        env_dict = kw['env']
        # see if KERNEL_LAUNCH_TIMEOUT was included from user
        self.kernel_launch_timeout = float(env_dict.get('KERNEL_LAUNCH_TIMEOUT', elyra_kernel_launch_timeout))

        # add the applicable kernel_id to the env dict
        env_dict['KERNEL_ID'] = self.kernel_id
        for k in env_pop_list:
            env_dict.pop(k, None)
        self.log.debug("BaseProcessProxy env: {}".format(kw['env']))

        # Represents the local process (from popen) if applicable.  Note that we could have local_proc = None even when
        # the subclass is a LocalProcessProxy (or YarnProcessProxy).  This will happen if the JKG is restarted and the
        # persisted kernel-sessions indicate that its now running on a different server.  In those case, we use the ip
        # member variable to determine if the persisted state is local or remote and use signals with the pid to
        # implement the poll, kill and send_signal methods.
        self.local_proc = None
        self.ip = None
        self.pid = 0