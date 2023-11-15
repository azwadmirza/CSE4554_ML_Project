    def parse(self):
        ''' create an options parser for bin/ansible '''

        self.parser = CLI.base_parser(
            usage = "usage: %%prog [%s] [--help] [options] ..." % "|".join(self.VALID_ACTIONS),
            epilog = "\nSee '%s <command> --help' for more information on a specific command.\n\n" % os.path.basename(sys.argv[0])
        )

        self.set_action()

        # options specific to actions
        if self.action == "delete":
            self.parser.set_usage("usage: %prog delete [options] github_user github_repo")
        elif self.action == "import":
            self.parser.set_usage("usage: %prog import [options] github_user github_repo")
            self.parser.add_option('--no-wait', dest='wait', action='store_false', default=True,
                help='Don\'t wait for import results.')
            self.parser.add_option('--branch', dest='reference',
                help='The name of a branch to import. Defaults to the repository\'s default branch (usually master)')
            self.parser.add_option('--status', dest='check_status', action='store_true', default=False,
                help='Check the status of the most recent import request for given github_user/github_repo.')
        elif self.action == "info":
            self.parser.set_usage("usage: %prog info [options] role_name[,version]")
        elif self.action == "init":
            self.parser.set_usage("usage: %prog init [options] role_name")
            self.parser.add_option('-p', '--init-path', dest='init_path', default="./",
                help='The path in which the skeleton role will be created. The default is the current working directory.')
            self.parser.add_option(
                '--offline', dest='offline', default=False, action='store_true',
                help="Don't query the galaxy API when creating roles")
        elif self.action == "install":
            self.parser.set_usage("usage: %prog install [options] [-r FILE | role_name(s)[,version] | scm+role_repo_url[,version] | tar_file(s)]")
            self.parser.add_option('-i', '--ignore-errors', dest='ignore_errors', action='store_true', default=False,
                help='Ignore errors and continue with the next specified role.')
            self.parser.add_option('-n', '--no-deps', dest='no_deps', action='store_true', default=False,
                help='Don\'t download roles listed as dependencies')
            self.parser.add_option('-r', '--role-file', dest='role_file',
                help='A file containing a list of roles to be imported')
        elif self.action == "remove":
            self.parser.set_usage("usage: %prog remove role1 role2 ...")
        elif self.action == "list":
            self.parser.set_usage("usage: %prog list [role_name]")
        elif self.action == "login":
            self.parser.set_usage("usage: %prog login [options]")
            self.parser.add_option('--github-token', dest='token', default=None,
                help='Identify with github token rather than username and password.')
        elif self.action == "search":
            self.parser.add_option('--platforms', dest='platforms',
                help='list of OS platforms to filter by')
            self.parser.add_option('--galaxy-tags', dest='tags',
                help='list of galaxy tags to filter by')
            self.parser.add_option('--author', dest='author',
                help='GitHub username')
            self.parser.set_usage("usage: %prog search [searchterm1 searchterm2] [--galaxy-tags galaxy_tag1,galaxy_tag2] [--platforms platform1,platform2] [--author username]")
        elif self.action == "setup":
            self.parser.set_usage("usage: %prog setup [options] source github_user github_repo secret")
            self.parser.add_option('--remove', dest='remove_id', default=None,
                help='Remove the integration matching the provided ID value. Use --list to see ID values.')
            self.parser.add_option('--list', dest="setup_list", action='store_true', default=False,
                help='List all of your integrations.')

        # options that apply to more than one action
        if not self.action in ("delete","import","init","login","setup"):
            # NOTE: while the option type=str, the default is a list, and the
            # callback will set the value to a list.
            self.parser.add_option('-p', '--roles-path', dest='roles_path',
                                   action="callback", callback=CLI.expand_paths,
                                   type=str, default=C.DEFAULT_ROLES_PATH,
                help='The path to the directory containing your roles. '
                     'The default is the roles_path configured in your '
                     'ansible.cfg file (/etc/ansible/roles if not configured)')

        if self.action in ("import","info","init","install","login","search","setup","delete"):
            self.parser.add_option('-s', '--server', dest='api_server', default=C.GALAXY_SERVER,
                help='The API server destination')
            self.parser.add_option('-c', '--ignore-certs', action='store_true', dest='ignore_certs', default=False,
                help='Ignore SSL certificate validation errors.')

        if self.action in ("init","install"):
            self.parser.add_option('-f', '--force', dest='force', action='store_true', default=False,
                help='Force overwriting an existing role')

        self.options, self.args =self.parser.parse_args()
        display.verbosity = self.options.verbosity
        self.galaxy = Galaxy(self.options)

        return True