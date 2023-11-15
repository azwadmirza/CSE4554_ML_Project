    def search(self, *args):
        """Searches package recipes and binaries in the local cache or in a remote.

        If you provide a pattern, then it will search for existing package recipes matching it.
        If a full reference is provided (pkg/0.1@user/channel) then the existing binary packages for
        that reference will be displayed.
        If no remote is specified, the serach will be done in the local cache.
        Search is case sensitive, exact case has to be used. For case insensitive file systems, like
        Windows, case sensitive search can be forced with '--case-sensitive'.
        """
        parser = argparse.ArgumentParser(description=self.search.__doc__, prog="conan search")
        parser.add_argument('pattern_or_reference', nargs='?', help=_PATTERN_OR_REFERENCE_HELP)
        parser.add_argument('-o', '--outdated', default=False, action='store_true',
                            help='Show only outdated from recipe packages')
        parser.add_argument('-q', '--query', default=None, action=OnceArgument, help=_QUERY_HELP)
        parser.add_argument('-r', '--remote', action=OnceArgument,
                            help="Remote to search in. '-r all' searches all remotes")
        parser.add_argument('--case-sensitive', default=False, action='store_true',
                            help='Make a case-sensitive search. Use it to guarantee case-sensitive '
                            'search in Windows or other case-insensitive file systems')
        parser.add_argument('--raw', default=False, action='store_true',
                            help='Print just the list of recipes')
        parser.add_argument('--table', action=OnceArgument,
                            help="Outputs html file with a table of binaries. Only valid for a "
                            "reference search")
        parser.add_argument("-j", "--json", default=None, action=OnceArgument,
                            help='json file path where the search information will be written to')
        args = parser.parse_args(*args)

        if args.table and args.json:
            raise ConanException("'--table' argument cannot be used together with '--json'")

        try:
            reference = ConanFileReference.loads(args.pattern_or_reference)
            if "*" in reference:
                # Fixes a version with only a wildcard (valid reference) but not real reference
                # e.j: conan search lib/*@lasote/stable
                reference = None
        except (TypeError, ConanException):
            reference = None

        cwd = os.getcwd()
        info = None

        try:
            if reference:
                info = self._conan.search_packages(reference, query=args.query, remote=args.remote,
                                                   outdated=args.outdated)
                # search is done for one reference
                self._outputer.print_search_packages(info["results"], reference, args.query,
                                                     args.table)
            else:
                if args.table:
                    raise ConanException("'--table' argument can only be used with a reference")

                self._check_query_parameter_and_get_reference(args.pattern_or_reference, args.query)

                info = self._conan.search_recipes(args.pattern_or_reference, remote=args.remote,
                                                  case_sensitive=args.case_sensitive)
                # Deprecate 2.0: Dirty check if search is done for all remotes or for remote "all"
                remote_registry = RemoteRegistry(self._client_cache.registry, None)
                all_remotes_search = ("all" not in (r.name for r in remote_registry.remotes) and
                                      args.remote == "all")

                self._outputer.print_search_references(info["results"], args.pattern_or_reference,
                                                       args.raw, all_remotes_search)
        except ConanException as exc:
            info = exc.info
            raise
        finally:
            if args.json and info:
                self._outputer.json_output(info, args.json, cwd)