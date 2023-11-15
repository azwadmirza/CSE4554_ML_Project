        def recursive_glob(treeroot, pattern):
            results = []
            for base, _, files in os.walk(treeroot):
                goodfiles = fnmatch.filter(files, pattern)
                results.extend(ek(os.path.join, base, f) for f in goodfiles)
            return results