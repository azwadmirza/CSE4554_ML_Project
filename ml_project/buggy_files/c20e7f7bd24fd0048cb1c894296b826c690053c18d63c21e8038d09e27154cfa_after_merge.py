    def __init__(self, module, user=None, cron_file=None):
        self.module = module
        self.user = user
        self.root = (os.getuid() == 0)
        self.lines = None
        self.ansible = "#Ansible: "
        self.n_existing = ''
        self.cron_cmd = self.module.get_bin_path('crontab', required=True)

        if cron_file:
            if os.path.isabs(cron_file):
                self.cron_file = cron_file
                self.b_cron_file = to_bytes(cron_file, errors='surrogate_or_strict')
            else:
                self.cron_file = os.path.join('/etc/cron.d', cron_file)
                self.b_cron_file = os.path.join(b'/etc/cron.d', to_bytes(cron_file, errors='surrogate_or_strict'))
        else:
            self.cron_file = None

        self.read()