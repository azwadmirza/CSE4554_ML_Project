def parse_cmdlineoptions(arglist):  # noqa: C901
    """Parse argument list and set global preferences"""
    global args, action, create_full_path, force, restore_timestr, remote_cmd
    global remote_schema, remove_older_than_string
    global user_mapping_filename, group_mapping_filename, \
        preserve_numerical_ids

    def sel_fl(filename):
        """Helper function for including/excluding filelists below"""
        try:
            return open(filename, "rb")  # files match paths hence bytes/bin
        except IOError:
            Log.FatalError("Error opening file %s" % filename)

    def normalize_path(path):
        """Used below to normalize the security paths before setting"""
        return rpath.RPath(Globals.local_connection, path).normalize().path

    try:
        optlist, args = getopt.getopt(arglist, "blr:sv:V", [
            "allow-duplicate-timestamps",
            "backup-mode", "calculate-average", "carbonfile",
            "check-destination-dir", "compare", "compare-at-time=",
            "compare-hash", "compare-hash-at-time=", "compare-full",
            "compare-full-at-time=", "create-full-path", "current-time=",
            "exclude=", "exclude-device-files", "exclude-fifos",
            "exclude-filelist=", "exclude-symbolic-links", "exclude-sockets",
            "exclude-filelist-stdin", "exclude-globbing-filelist=",
            "exclude-globbing-filelist-stdin", "exclude-mirror=",
            "exclude-other-filesystems", "exclude-regexp=",
            "exclude-if-present=", "exclude-special-files", "force",
            "group-mapping-file=", "include=", "include-filelist=",
            "include-filelist-stdin", "include-globbing-filelist=",
            "include-globbing-filelist-stdin", "include-regexp=",
            "include-special-files", "include-symbolic-links", "list-at-time=",
            "list-changed-since=", "list-increments", "list-increment-sizes",
            "never-drop-acls", "max-file-size=", "min-file-size=", "no-acls",
            "no-carbonfile", "no-compare-inode", "no-compression",
            "no-compression-regexp=", "no-eas", "no-file-statistics",
            "no-hard-links", "null-separator", "override-chars-to-quote=",
            "parsable-output", "preserve-numerical-ids", "print-statistics",
            "remote-cmd=", "remote-schema=", "remote-tempdir=",
            "remove-older-than=", "restore-as-of=", "restrict=",
            "restrict-read-only=", "restrict-update-only=", "server",
            "ssh-no-compression", "tempdir=", "terminal-verbosity=",
            "test-server", "use-compatible-timestamps", "user-mapping-file=",
            "verbosity=", "verify", "verify-at-time=", "version", "no-fsync"
        ])
    except getopt.error as e:
        commandline_error("Bad commandline options: " + str(e))

    for opt, arg in optlist:
        if opt == "-b" or opt == "--backup-mode":
            action = "backup"
        elif opt == "--calculate-average":
            action = "calculate-average"
        elif opt == "--carbonfile":
            Globals.set("carbonfile_active", 1)
        elif opt == "--check-destination-dir":
            action = "check-destination-dir"
        elif opt in ("--compare", "--compare-at-time", "--compare-hash",
                     "--compare-hash-at-time", "--compare-full",
                     "--compare-full-at-time"):
            if opt[-8:] == "-at-time":
                restore_timestr, opt = arg, opt[:-8]
            else:
                restore_timestr = "now"
            action = opt[2:]
        elif opt == "--create-full-path":
            create_full_path = 1
        elif opt == "--current-time":
            Globals.set_integer('current_time', arg)
        elif (opt == "--exclude" or opt == "--exclude-device-files"
              or opt == "--exclude-fifos"
              or opt == "--exclude-other-filesystems"
              or opt == "--exclude-regexp" or opt == "--exclude-if-present"
              or opt == "--exclude-special-files" or opt == "--exclude-sockets"
              or opt == "--exclude-symbolic-links"):
            select_opts.append((opt, arg))
        elif opt == "--exclude-filelist":
            select_opts.append((opt, arg))
            select_files.append(sel_fl(arg))
        elif opt == "--exclude-filelist-stdin":
            select_opts.append(("--exclude-filelist", "standard input"))
            select_files.append(sys.stdin.buffer)
        elif opt == "--exclude-globbing-filelist":
            select_opts.append((opt, arg))
            select_files.append(sel_fl(arg))
        elif opt == "--exclude-globbing-filelist-stdin":
            select_opts.append(("--exclude-globbing-filelist",
                                "standard input"))
            select_files.append(sys.stdin.buffer)
        elif opt == "--force":
            force = 1
        elif opt == "--group-mapping-file":
            group_mapping_filename = os.fsencode(arg)
        elif (opt == "--include" or opt == "--include-special-files"
              or opt == "--include-symbolic-links"):
            select_opts.append((opt, arg))
        elif opt == "--include-filelist":
            select_opts.append((opt, arg))
            select_files.append(sel_fl(arg))
        elif opt == "--include-filelist-stdin":
            select_opts.append(("--include-filelist", "standard input"))
            select_files.append(sys.stdin.buffer)
        elif opt == "--include-globbing-filelist":
            select_opts.append((opt, arg))
            select_files.append(sel_fl(arg))
        elif opt == "--include-globbing-filelist-stdin":
            select_opts.append(("--include-globbing-filelist",
                                "standard input"))
            select_files.append(sys.stdin.buffer)
        elif opt == "--include-regexp":
            select_opts.append((opt, arg))
        elif opt == "--list-at-time":
            restore_timestr, action = arg, "list-at-time"
        elif opt == "--list-changed-since":
            restore_timestr, action = arg, "list-changed-since"
        elif opt == "-l" or opt == "--list-increments":
            action = "list-increments"
        elif opt == '--list-increment-sizes':
            action = 'list-increment-sizes'
        elif opt == "--max-file-size":
            select_opts.append((opt, arg))
        elif opt == "--min-file-size":
            select_opts.append((opt, arg))
        elif opt == "--never-drop-acls":
            Globals.set("never_drop_acls", 1)
        elif opt == "--no-acls":
            Globals.set("acls_active", 0)
            Globals.set("win_acls_active", 0)
        elif opt == "--no-carbonfile":
            Globals.set("carbonfile_active", 0)
        elif opt == "--no-compare-inode":
            Globals.set("compare_inode", 0)
        elif opt == "--no-compression":
            Globals.set("compression", None)
        elif opt == "--no-compression-regexp":
            Globals.set("no_compression_regexp_string", os.fsencode(arg))
        elif opt == "--no-eas":
            Globals.set("eas_active", 0)
        elif opt == "--no-file-statistics":
            Globals.set('file_statistics', 0)
        elif opt == "--no-hard-links":
            Globals.set('preserve_hardlinks', 0)
        elif opt == "--null-separator":
            Globals.set("null_separator", 1)
        elif opt == "--override-chars-to-quote":
            Globals.set('chars_to_quote', os.fsencode(arg))
        elif opt == "--parsable-output":
            Globals.set('parsable_output', 1)
        elif opt == "--preserve-numerical-ids":
            preserve_numerical_ids = 1
        elif opt == "--print-statistics":
            Globals.set('print_statistics', 1)
        elif opt == "-r" or opt == "--restore-as-of":
            restore_timestr, action = arg, "restore-as-of"
        elif opt == "--remote-cmd":
            remote_cmd = os.fsencode(arg)
        elif opt == "--remote-schema":
            remote_schema = os.fsencode(arg)
        elif opt == "--remote-tempdir":
            Globals.remote_tempdir = os.fsencode(arg)
        elif opt == "--remove-older-than":
            remove_older_than_string = arg
            action = "remove-older-than"
        elif opt == "--no-resource-forks":
            Globals.set('resource_forks_active', 0)
        elif opt == "--restrict":
            Globals.restrict_path = normalize_path(arg)
        elif opt == "--restrict-read-only":
            Globals.security_level = "read-only"
            Globals.restrict_path = normalize_path(arg)
        elif opt == "--restrict-update-only":
            Globals.security_level = "update-only"
            Globals.restrict_path = normalize_path(arg)
        elif opt == "-s" or opt == "--server":
            action = "server"
            Globals.server = 1
        elif opt == "--ssh-no-compression":
            Globals.set('ssh_compression', None)
        elif opt == "--tempdir":
            if (not os.path.isdir(arg)):
                Log.FatalError("Temporary directory '%s' doesn't exist." % arg)
            tempfile.tempdir = os.fsencode(arg)
        elif opt == "--terminal-verbosity":
            Log.setterm_verbosity(arg)
        elif opt == "--test-server":
            action = "test-server"
        elif opt == "--use-compatible-timestamps":
            Globals.set("use_compatible_timestamps", 1)
        elif opt == "--allow-duplicate-timestamps":
            Globals.set("allow_duplicate_timestamps", True)
        elif opt == "--user-mapping-file":
            user_mapping_filename = os.fsencode(arg)
        elif opt == "-v" or opt == "--verbosity":
            Log.setverbosity(arg)
        elif opt == "--verify":
            action, restore_timestr = "verify", "now"
        elif opt == "--verify-at-time":
            action, restore_timestr = "verify", arg
        elif opt == "-V" or opt == "--version":
            print("rdiff-backup " + Globals.version)
            sys.exit(0)
        elif opt == "--no-fsync":
            Globals.do_fsync = False
        else:
            Log.FatalError("Unknown option %s" % opt)
    Log("Using rdiff-backup version %s" % (Globals.version), 4)
    Log("\twith %s %s version %s" % (
        sys.implementation.name,
        sys.executable,
        platform.python_version()), 4)
    Log("\ton %s, fs encoding %s" % (platform.platform(), sys.getfilesystemencoding()), 4)