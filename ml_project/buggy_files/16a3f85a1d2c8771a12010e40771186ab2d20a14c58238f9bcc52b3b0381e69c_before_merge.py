    def __init__(
            self,
            opts,
            argv,
            id_,
            host,
            user=None,
            port=None,
            passwd=None,
            priv=None,
            timeout=None,
            sudo=False,
            tty=False,
            mods=None,
            fsclient=None,
            **kwargs):
        self.opts = opts
        if kwargs.get('wipe'):
            self.wipe = 'False'
        else:
            self.wipe = 'True' if self.opts.get('wipe_ssh') else 'False'
        if kwargs.get('thin_dir'):
            self.thin_dir = kwargs['thin_dir']
        else:
            if user:
                thin_dir = DEFAULT_THIN_DIR.replace('%%USER%%', user)
            else:
                thin_dir = DEFAULT_THIN_DIR.replace('%%USER%%', 'root')
            self.thin_dir = thin_dir.replace(
                '%%FQDNUUID%%',
                uuid.uuid3(uuid.NAMESPACE_DNS,
                           salt.utils.network.get_fqhostname()).hex[:6]
            )
        self.opts['thin_dir'] = self.thin_dir
        self.fsclient = fsclient
        self.context = {'master_opts': self.opts,
                        'fileclient': self.fsclient}

        if isinstance(argv, string_types):
            self.argv = [argv]
        else:
            self.argv = argv

        self.fun, self.args, self.kwargs = self.__arg_comps()
        self.id = id_

        self.mods = mods if isinstance(mods, dict) else {}
        args = {'host': host,
                'user': user,
                'port': port,
                'passwd': passwd,
                'priv': priv,
                'timeout': timeout,
                'sudo': sudo,
                'tty': tty,
                'mods': self.mods}
        self.minion_config = yaml.dump(
                {
                    'root_dir': os.path.join(self.thin_dir, 'running_data'),
                    'id': self.id,
                    'sock_dir': '/',
                }, width=1000).strip()
        self.target = kwargs
        self.target.update(args)
        self.serial = salt.payload.Serial(opts)
        self.wfuncs = salt.loader.ssh_wrapper(opts, None, self.context)
        self.shell = salt.client.ssh.shell.Shell(opts, **args)