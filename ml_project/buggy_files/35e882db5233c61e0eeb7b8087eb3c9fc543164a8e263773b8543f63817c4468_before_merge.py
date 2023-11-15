    def __init__(self, opts):
        pull_sock = os.path.join(opts['sock_dir'], 'master_event_pull.ipc')
        if os.path.isfile(pull_sock) and HAS_ZMQ:
            self.event = salt.utils.event.get_event(
                    'master',
                    opts['sock_dir'],
                    opts['transport'],
                    opts=opts,
                    listen=False)
        else:
            self.event = None
        self.opts = opts
        self.opts['_ssh_version'] = ssh_version()
        self.tgt_type = self.opts['selected_target_option'] \
                if self.opts['selected_target_option'] else 'glob'
        self.roster = salt.roster.Roster(opts, opts.get('roster'))
        self.targets = self.roster.targets(
                self.opts['tgt'],
                self.tgt_type)
        priv = self.opts.get(
                'ssh_priv',
                os.path.join(
                    self.opts['pki_dir'],
                    'ssh',
                    'salt-ssh.rsa'
                    )
                )
        if not os.path.isfile(priv):
            try:
                salt.client.ssh.shell.gen_key(priv)
            except OSError:
                raise salt.exceptions.SaltClientError('salt-ssh could not be run because it could not generate keys.\n\nYou can probably resolve this by executing this script with increased permissions via sudo or by running as root.\nYou could also use the \'-c\' option to supply a configuration directory that you have permissions to read and write to.')
        self.defaults = {
            'user': self.opts.get(
                'ssh_user',
                salt.config.DEFAULT_MASTER_OPTS['ssh_user']
            ),
            'port': self.opts.get(
                'ssh_port',
                salt.config.DEFAULT_MASTER_OPTS['ssh_port']
            ),
            'passwd': self.opts.get(
                'ssh_passwd',
                salt.config.DEFAULT_MASTER_OPTS['ssh_passwd']
            ),
            'priv': priv,
            'timeout': self.opts.get(
                'ssh_timeout',
                salt.config.DEFAULT_MASTER_OPTS['ssh_timeout']
            ) + self.opts.get(
                'timeout',
                salt.config.DEFAULT_MASTER_OPTS['timeout']
            ),
            'sudo': self.opts.get(
                'ssh_sudo',
                salt.config.DEFAULT_MASTER_OPTS['ssh_sudo']
            ),
        }
        if self.opts.get('rand_thin_dir'):
            self.defaults['thin_dir'] = os.path.join(
                    '/tmp',
                    '.{0}'.format(uuid.uuid4().hex[:6]))
            self.opts['wipe_ssh'] = 'True'
        self.serial = salt.payload.Serial(opts)
        self.returners = salt.loader.returners(self.opts, {})
        self.fsclient = salt.fileclient.FSClient(self.opts)
        self.mods = mod_data(self.fsclient)