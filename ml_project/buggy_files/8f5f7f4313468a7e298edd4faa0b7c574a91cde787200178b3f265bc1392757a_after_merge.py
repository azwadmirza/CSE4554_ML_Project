        def dedupe_pkgs_dir_contents(pkgs_dir_contents):
            # if both 'six-1.10.0-py35_0/' and 'six-1.10.0-py35_0.tar.bz2' are in pkgs_dir,
            #   only 'six-1.10.0-py35_0.tar.bz2' will be in the return contents
            if not pkgs_dir_contents:
                return []

            contents = []

            def _process(x, y):
                if x + CONDA_TARBALL_EXTENSION != y:
                    contents.append(x)
                return y

            last = reduce(_process, sorted(pkgs_dir_contents))
            _process(last, contents and contents[-1] or '')
            return contents