    def search(self, *args):
        """Searches package recipes and binaries in the local cache or in a remote.

        If you provide a pattern, then it will search for existing package
        recipes matching it.  If a full reference is provided
        (pkg/0.1@user/channel) then the existing binary packages for that
        reference will be displayed.  If no remote is specified, the search
        will be done in the local cache.  Search is case sensitive, exact case
        has to be used. For case insensitive file systems, like Windows, case
        sensitive search can be forced with '--case-sensitive'.
        """
        parser = argparse.ArgumentParser(description=self.search.__doc__, prog="conan search")
        parser.add_argument('pattern_or_reference', nargs='?', help=_PATTERN_OR_REFERENCE_HELP)
        parser.add_argument('-o', '--outdated', default=False, action='store_true',
                            help="Show only outdated from recipe packages. "
                                 "This flag can only be used with a reference")
        parser.add_argument('-q', '--query', default=None, action=OnceArgument, help=_QUERY_HELP)
        parser.add_argument('-r', '--remote', action=OnceArgument,
                            help="Remote to search in. '-r all' searches all remotes")
        parser.add_argument('--case-sensitive', default=False, action='store_true',
                            help='Make a case-sensitive search. Use it to guarantee '
                                 'case-sensitive '
                            'search in Windows or other case-insensitive file systems')
        parser.add_argument('--raw', default=False, action='store_true',
                            help='Print just the list of recipes')
        parser.add_argument('--table', action=OnceArgument,
                            help="Outputs html file with a table of binaries. Only valid for a "
                            "reference search")
        parser.add_argument("-j", "--json", default=None, action=OnceArgument,
                            help='json file path where the search information will be written to')
        parser.add_argument("-rev", "--revisions", default=False, action='store_true',
                            help='Get a list of revisions for a reference or a '
                                 'package reference.')

        args = parser.parse_args(*args)

        if args.revisions and not self._cache.config.revisions_enabled:
            raise ConanException("The client doesn't have the revisions feature enabled."
                                 " Enable this feature setting to '1' the environment variable"
                                 " 'CONAN_REVISIONS_ENABLED' or the config value"
                                 " 'general.revisions_enabled' in your conan.conf file")

        if args.table and args.json:
            raise ConanException("'--table' argument cannot be used together with '--json'")

        try:
            ref = ConanFileReference.loads(args.pattern_or_reference)
            if "*" in ref:
                # Fixes a version with only a wildcard (valid reference) but not real reference
                # e.g.: conan search lib/*@lasote/stable
                ref = None
        except (TypeError, ConanException):
            ref = None
            if args.query:
                raise ConanException("-q parameter only allowed with a valid recipe reference, "
                                     "not with a pattern")

        cwd = os.getcwd()
        info = None

        try:
            if args.revisions:
                try:
                    pref = PackageReference.loads(args.pattern_or_reference)
                except (TypeError, ConanException):
                    pass
                else:
                    info = self._conan.get_package_revisions(pref.full_repr(),
                                                             remote_name=args.remote)

                if not info:
                    if not ref:
                        msg = "With --revision, specify a reference (e.g {ref}) or a package " \
                              "reference with " \
                              "recipe revision (e.g {ref}#3453453453:d50a0d523d98c15bb147b18f" \
                              "a7d203887c38be8b)".format(ref=_REFERENCE_EXAMPLE)
                        raise ConanException(msg)
                    info = self._conan.get_recipe_revisions(ref.full_repr(),
                                                            remote_name=args.remote)
                self._outputer.print_revisions(ref, info, remote_name=args.remote)
                return

            if ref:
                info = self._conan.search_packages(ref.full_repr(), query=args.query,
                                                   remote_name=args.remote,
                                                   outdated=args.outdated)
                # search is done for one reference
                self._outputer.print_search_packages(info["results"], ref, args.query,
                                                     args.table, outdated=args.outdated)
            else:
                if args.table:
                    raise ConanException("'--table' argument can only be used with a reference")
                elif args.outdated:
                    raise ConanException("'--outdated' argument can only be used with a reference")

                info = self._conan.search_recipes(args.pattern_or_reference,
                                                  remote_name=args.remote,
                                                  case_sensitive=args.case_sensitive)
                # Deprecate 2.0: Dirty check if search is done for all remotes or for remote "all"
                try:
                    remote_all = self._conan.get_remote_by_name("all")
                except NoRemoteAvailable:
                    remote_all = None
                all_remotes_search = (remote_all is None and args.remote == "all")

                self._outputer.print_search_references(info["results"], args.pattern_or_reference,
                                                       args.raw, all_remotes_search)
        except ConanException as exc:
            info = exc.info
            raise
        finally:
            if args.json and info:
                self._outputer.json_output(info, args.json, cwd)