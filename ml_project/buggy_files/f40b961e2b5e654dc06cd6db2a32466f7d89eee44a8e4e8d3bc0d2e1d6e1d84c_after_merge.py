    def run(self, terms, variables, **kwargs):

        result = None
        anydict = False
        skip = False

        for term in terms:
            if isinstance(term, dict):
                anydict = True

        total_search = []
        if anydict:
            for term in terms:
                if isinstance(term, dict):
                    files = term.get('files', [])
                    paths = term.get('paths', [])
                    skip  = boolean(term.get('skip', False))

                    filelist = files
                    if isinstance(files, basestring):
                        files = files.replace(',', ' ')
                        files = files.replace(';', ' ')
                        filelist = files.split(' ')

                    pathlist = paths
                    if paths:
                        if isinstance(paths, basestring):
                            paths = paths.replace(',', ' ')
                            paths = paths.replace(':', ' ')
                            paths = paths.replace(';', ' ')
                            pathlist = paths.split(' ')

                    if not pathlist:
                        total_search = filelist
                    else:
                        for path in pathlist:
                            for fn in filelist:
                                f = os.path.join(path, fn)
                                total_search.append(f)
                else:
                    total_search.append(term)
        else:
            total_search = self._flatten(terms)

        roledir = variables.get('roledir')
        for fn in total_search:
            try:
                fn = self._templar.template(fn)
            except (AnsibleUndefinedVariable, UndefinedError) as e:
                continue

            if os.path.isabs(fn) and os.path.exists(fn):
                return [fn]
            else:
                if roledir is not None:
                    # check the templates and vars directories too,if they exist
                    for subdir in ('templates', 'vars', 'files'):
                        path = self._loader.path_dwim_relative(roledir, subdir, fn)
                        if os.path.exists(path):
                            return [path]

                # if none of the above were found, just check the
                # current filename against the current dir
                path = self._loader.path_dwim(fn)
                if os.path.exists(path):
                    return [path]
        else:
            if skip:
                return []
            else:
                raise AnsibleLookupError("No file was found when using with_first_found. Use the 'skip: true' option to allow this task to be skipped if no files are found")