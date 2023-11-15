    def config(self, *args):
        """
        Manages Conan configuration.

        Used to edit conan.conf, or install config files.
        """
        parser = argparse.ArgumentParser(description=self.config.__doc__,
                                         prog="conan config",
                                         formatter_class=SmartFormatter)

        subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
        subparsers.required = True

        get_subparser = subparsers.add_parser('get', help='Get the value of configuration item')
        home_subparser = subparsers.add_parser('home', help='Retrieve the Conan home directory')
        install_subparser = subparsers.add_parser('install', help='Install a full configuration '
                                                                  'from a local or remote zip file')
        rm_subparser = subparsers.add_parser('rm', help='Remove an existing config element')
        set_subparser = subparsers.add_parser('set', help='Set a value for a configuration item')
        init_subparser = subparsers.add_parser('init', help='Initializes Conan configuration files')

        get_subparser.add_argument("item", nargs="?", help="Item to print")
        home_subparser.add_argument("-j", "--json", default=None, action=OnceArgument,
                                    help='json file path where the config home will be written to')
        install_subparser.add_argument("item", nargs="?",
                                       help="git repository, local folder or zip file (local or "
                                       "http) where the configuration is stored")

        install_subparser.add_argument("--verify-ssl", nargs="?", default="True",
                                       help='Verify SSL connection when downloading file')
        install_subparser.add_argument("--type", "-t", choices=["git"],
                                       help='Type of remote config')
        install_subparser.add_argument("--args", "-a",
                                       help='String with extra arguments for "git clone"')
        install_subparser.add_argument("-sf", "--source-folder",
                                       help='Install files only from a source subfolder from the '
                                       'specified origin')
        install_subparser.add_argument("-tf", "--target-folder",
                                       help='Install to that path in the conan cache')
        install_subparser.add_argument("-l", "--list", default=False, action='store_true',
                                       help='List stored configuration origins')
        install_subparser.add_argument("-r", "--remove", type=int,
                                       help='Remove configuration origin by index in list (index '
                                            'provided by --list argument)')
        rm_subparser.add_argument("item", help="Item to remove")
        set_subparser.add_argument("item", help="'item=value' to set")
        init_subparser.add_argument('-f', '--force', default=False, action='store_true',
                                    help='Overwrite existing Conan configuration files')

        args = parser.parse_args(*args)

        if args.subcommand == "set":
            try:
                key, value = args.item.split("=", 1)
            except ValueError:
                if "hooks." in args.item:
                    key, value = args.item.split("=", 1)[0], None
                else:
                    raise ConanException("Please specify 'key=value'")
            return self._conan.config_set(key, value)
        elif args.subcommand == "get":
            return self._conan.config_get(args.item)
        elif args.subcommand == "rm":
            return self._conan.config_rm(args.item)
        elif args.subcommand == "home":
            conan_home = self._conan.config_home()
            self._out.info(conan_home)
            if args.json:
                self._outputer.json_output({"home": conan_home}, args.json, os.getcwd())
            return conan_home
        elif args.subcommand == "install":
            if args.list:
                configs = self._conan.config_install_list()
                for index, config in enumerate(configs):
                    self._out.writeln("%s: %s" % (index, config))
                return
            elif args.remove is not None:
                self._conan.config_install_remove(index=args.remove)
                return
            verify_ssl = get_bool_from_text(args.verify_ssl)
            return self._conan.config_install(args.item, verify_ssl, args.type, args.args,
                                              source_folder=args.source_folder,
                                              target_folder=args.target_folder)
        elif args.subcommand == 'init':
            return self._conan.config_init(force=args.force)