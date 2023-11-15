    def run(self):

        super(ConsoleCLI, self).run()

        sshpass    = None
        becomepass = None
        vault_pass = None

        # hosts
        if len(self.args) != 1:
            self.pattern = 'all'
        else:
            self.pattern = self.args[0]
        self.options.cwd = self.pattern

        # dynamically add modules as commands
        self.modules = self.list_modules()
        for module in self.modules:
            setattr(self, 'do_' + module, lambda arg, module=module: self.default(module + ' ' + arg))
            setattr(self, 'help_' + module, lambda module=module: self.helpdefault(module))

        self.normalize_become_options()
        (sshpass, becomepass) = self.ask_passwords()
        self.passwords = { 'conn_pass': sshpass, 'become_pass': becomepass }

        self.loader = DataLoader()

        if self.options.vault_password_file:
            # read vault_pass from a file
            vault_pass = CLI.read_vault_password_file(self.options.vault_password_file, loader=self.loader)
            self.loader.set_vault_password(vault_pass)
        elif self.options.ask_vault_pass:
            vault_pass = self.ask_vault_passwords()[0]
            self.loader.set_vault_password(vault_pass)

        self.variable_manager = VariableManager()
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.options.inventory)
        self.variable_manager.set_inventory(self.inventory)

        no_hosts = False
        if len(self.inventory.list_hosts()) == 0:
            # Empty inventory
            no_hosts = True
            display.warning("provided hosts list is empty, only localhost is available")

        self.inventory.subset(self.options.subset)
        hosts = self.inventory.list_hosts(self.pattern)
        if len(hosts) == 0 and not no_hosts:
            raise AnsibleError("Specified hosts and/or --limit does not match any hosts")

        self.groups = self.inventory.list_groups()
        self.hosts = [x.name for x in hosts]

        # This hack is to work around readline issues on a mac:
        #  http://stackoverflow.com/a/7116997/541202
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        histfile = os.path.join(os.path.expanduser("~"), ".ansible-console_history")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass

        atexit.register(readline.write_history_file, histfile)
        self.set_prompt()
        self.cmdloop()