    def _refresh_file_mapping(self):
        """
        refresh the mapping of the FS on disk
        """
        # map of suffix to description for imp
        if (
            self.opts.get("cython_enable", True) is True
            and ".pyx" not in self.suffix_map
        ):
            try:
                global pyximport
                pyximport = __import__("pyximport")  # pylint: disable=import-error
                pyximport.install()
                # add to suffix_map so file_mapping will pick it up
                self.suffix_map[".pyx"] = tuple()
                if ".pyx" not in self.suffix_order:
                    self.suffix_order.append(".pyx")
            except ImportError:
                log.info(
                    "Cython is enabled in the options but not present "
                    "in the system path. Skipping Cython modules."
                )
        # Allow for zipimport of modules
        if (
            self.opts.get("enable_zip_modules", True) is True
            and ".zip" not in self.suffix_map
        ):
            self.suffix_map[".zip"] = tuple()
            if ".zip" not in self.suffix_order:
                self.suffix_order.append(".zip")
        # allow for module dirs
        if USE_IMPORTLIB:
            self.suffix_map[""] = ("", "", MODULE_KIND_PKG_DIRECTORY)
        else:
            self.suffix_map[""] = ("", "", imp.PKG_DIRECTORY)

        # create mapping of filename (without suffix) to (path, suffix)
        # The files are added in order of priority, so order *must* be retained.
        self.file_mapping = salt.utils.odict.OrderedDict()

        opt_match = []

        def _replace_pre_ext(obj):
            """
            Hack so we can get the optimization level that we replaced (if
            any) out of the re.sub call below. We use a list here because
            it is a persistent data structure that we will be able to
            access after re.sub is called.
            """
            opt_match.append(obj)
            return ""

        for mod_dir in self.module_dirs:
            try:
                # Make sure we have a sorted listdir in order to have
                # expectable override results
                files = sorted(x for x in os.listdir(mod_dir) if x != "__pycache__")
            except OSError:
                continue  # Next mod_dir
            try:
                pycache_files = [
                    os.path.join("__pycache__", x)
                    for x in sorted(os.listdir(os.path.join(mod_dir, "__pycache__")))
                ]
            except OSError:
                pass
            else:
                files.extend(pycache_files)

            for filename in files:
                try:
                    dirname, basename = os.path.split(filename)
                    if basename.startswith("_"):
                        # skip private modules
                        # log messages omitted for obviousness
                        continue  # Next filename
                    f_noext, ext = os.path.splitext(basename)
                    f_noext = PY3_PRE_EXT.sub(_replace_pre_ext, f_noext)
                    try:
                        opt_level = int(opt_match.pop().group(1).rsplit("-", 1)[-1])
                    except (AttributeError, IndexError, ValueError):
                        # No regex match or no optimization level matched
                        opt_level = 0
                    try:
                        opt_index = self.opts["optimization_order"].index(opt_level)
                    except KeyError:
                        log.trace(
                            "Disallowed optimization level %d for module "
                            "name '%s', skipping. Add %d to the "
                            "'optimization_order' config option if you "
                            "do not want to ignore this optimization "
                            "level.",
                            opt_level,
                            f_noext,
                            opt_level,
                        )
                        continue

                    # make sure it is a suffix we support
                    if ext not in self.suffix_map:
                        continue  # Next filename
                    if f_noext in self.disabled:
                        log.trace(
                            "Skipping %s, it is disabled by configuration", filename
                        )
                        continue  # Next filename
                    fpath = os.path.join(mod_dir, filename)
                    # if its a directory, lets allow us to load that
                    if ext == "":
                        # is there something __init__?
                        subfiles = os.listdir(fpath)
                        for suffix in self.suffix_order:
                            if "" == suffix:
                                continue  # Next suffix (__init__ must have a suffix)
                            init_file = "__init__{}".format(suffix)
                            if init_file in subfiles:
                                break
                        else:
                            continue  # Next filename

                    try:
                        curr_ext = self.file_mapping[f_noext][1]
                        curr_opt_index = self.file_mapping[f_noext][2]
                    except KeyError:
                        pass
                    else:
                        if "" in (curr_ext, ext) and curr_ext != ext:
                            log.error(
                                "Module/package collision: '%s' and '%s'",
                                fpath,
                                self.file_mapping[f_noext][0],
                            )

                        if six.PY3 and ext == ".pyc" and curr_ext == ".pyc":
                            # Check the optimization level
                            if opt_index >= curr_opt_index:
                                # Module name match, but a higher-priority
                                # optimization level was already matched, skipping.
                                continue
                        elif not curr_ext or self.suffix_order.index(
                            ext
                        ) >= self.suffix_order.index(curr_ext):
                            # Match found but a higher-priorty match already
                            # exists, so skip this.
                            continue

                    if six.PY3 and not dirname and ext == ".pyc":
                        # On Python 3, we should only load .pyc files from the
                        # __pycache__ subdirectory (i.e. when dirname is not an
                        # empty string).
                        continue

                    # Made it this far - add it
                    self.file_mapping[f_noext] = (fpath, ext, opt_index)

                except OSError:
                    continue
        for smod in self.static_modules:
            f_noext = smod.split(".")[-1]
            self.file_mapping[f_noext] = (smod, ".o", 0)