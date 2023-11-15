def get_help_dict():
    # this is a function so that most of the time it's not evaluated and loaded into memory
    return frozendict({
        'add_anaconda_token': dals("""
            In conjunction with the anaconda command-line client (installed with
            `conda install anaconda-client`), and following logging into an Anaconda
            Server API site using `anaconda login`, automatically apply a matching
            private token to enable access to private packages and channels.
            """),
        'add_pip_as_python_dependency': dals("""
            Add pip, wheel and setuptools as dependencies of python. This ensures pip,
            wheel and setuptools will always be installed any time python is installed.
            """),
        'aggressive_update_packages': dals("""
            A list of packages that, if installed, are always updated to the latest possible
            version.
            """),
        'allow_non_channel_urls': dals("""
            Warn, but do not fail, when conda detects a channel url is not a valid channel.
            """),
        'allow_softlinks': dals("""
            When allow_softlinks is True, conda uses hard-links when possible, and soft-links
            (symlinks) when hard-links are not possible, such as when installing on a
            different filesystem than the one that the package cache is on. When
            allow_softlinks is False, conda still uses hard-links when possible, but when it
            is not possible, conda copies files. Individual packages can override
            this setting, specifying that certain files should never be soft-linked (see the
            no_link option in the build recipe documentation).
            """),
        'always_copy': dals("""
            Register a preference that files be copied into a prefix during install rather
            than hard-linked.
            """),
        'always_softlink': dals("""
            Register a preference that files be soft-linked (symlinked) into a prefix during
            install rather than hard-linked. The link source is the 'pkgs_dir' package cache
            from where the package is being linked. WARNING: Using this option can result in
            corruption of long-lived conda environments. Package caches are *caches*, which
            means there is some churn and invalidation. With this option, the contents of
            environments can be switched out (or erased) via operations on other environments.
            """),
        'always_yes': dals("""
            Automatically choose the 'yes' option whenever asked to proceed with a conda
            operation, such as when running `conda install`.
            """),
        'anaconda_upload': dals("""
            Automatically upload packages built with conda build to anaconda.org.
            """),
        'auto_update_conda': dals("""
            Automatically update conda when a newer or higher priority version is detected.
            """),
        'changeps1': dals("""
            When using activate, change the command prompt ($PS1) to include the
            activated environment.
            """),
        'channel_alias': dals("""
            The prepended url location to associate with channel names.
            """),
        'channel_priority': dals("""
            When True, the solver is instructed to prefer channel order over package
            version. When False, the solver is instructed to give package version
            preference over channel priority.
            """),
        'channels': dals("""
            The list of conda channels to include for relevant operations.
            """),
        'client_ssl_cert': dals("""
            A path to a single file containing a private key and certificate (e.g. .pem
            file). Alternately, use client_ssl_cert_key in conjuction with client_ssl_cert
            for individual files.
            """),
        'client_ssl_cert_key': dals("""
            Used in conjunction with client_ssl_cert for a matching key file.
            """),
        'clobber': dals("""
            Allow clobbering of overlapping file paths within packages, and suppress
            related warnings. Overrides the path_conflict configuration value when
            set to 'warn' or 'prevent'.
            """),
        'create_default_packages': dals("""
            Packages that are by default added to a newly created environments.
            """),  # TODO: This is a bad parameter name. Consider an alternate.
        'custom_channels': dals("""
            A map of key-value pairs where the key is a channel name and the value is
            a channel location. Channels defined here override the default
            'channel_alias' value. The channel name (key) is not included in the channel
            location (value).  For example, to override the location of the 'conda-forge'
            channel where the url to repodata is
            https://anaconda-repo.dev/packages/conda-forge/linux-64/repodata.json, add an
            entry 'conda-forge: https://anaconda-repo.dev/packages'.
            """),
        'custom_multichannels': dals("""
            A multichannel is a metachannel composed of multiple channels. The two reserved
            multichannels are 'defaults' and 'local'. The 'defaults' multichannel is
            customized using the 'default_channels' parameter. The 'local'
            multichannel is a list of file:// channel locations where conda-build stashes
            successfully-built packages.  Other multichannels can be defined with
            custom_multichannels, where the key is the multichannel name and the value is
            a list of channel names and/or channel urls.
            """),
        'default_channels': dals("""
            The list of channel names and/or urls used for the 'defaults' multichannel.
            """),
        # 'default_python': dals("""
        #     specifies the default major & minor version of Python to be used when
        #     building packages with conda-build. Also used to determine the major
        #     version of Python (2/3) to be used in new environments. Defaults to
        #     the version used by conda itself.
        #     """),
        'disallow': dals("""
            Package specifications to disallow installing. The default is to allow
            all packages.
            """),
        'download_only': dals("""
            Solve an environment and ensure package caches are populated, but exit
            prior to unlinking and linking packages into the prefix
            """),
        'envs_dirs': dals("""
            The list of directories to search for named environments. When creating a new
            named environment, the environment will be placed in the first writable
            location.
            """),
        'force': dals("""
            Override any of conda's objections and safeguards for installing packages and
            potentially breaking environments. Also re-installs the package, even if the
            package is already installed. Implies --no-deps.
            """),
        # 'force_32bit': dals("""
        #     CONDA_FORCE_32BIT should only be used when running conda-build (in order
        #     to build 32-bit packages on a 64-bit system).  We don't want to mention it
        #     in the documentation, because it can mess up a lot of things.
        #     """),
        'json': dals("""
            Ensure all output written to stdout is structured json.
            """),
        'local_repodata_ttl': dals("""
            For a value of False or 0, always fetch remote repodata (HTTP 304 responses
            respected). For a value of True or 1, respect the HTTP Cache-Control max-age
            header. Any other positive integer values is the number of seconds to locally
            cache repodata before checking the remote server for an update.
            """),
        'max_shlvl': dals("""
            The maximum number of stacked active conda environments.
            """),
        'migrated_channel_aliases': dals("""
            A list of previously-used channel_alias values, useful for example when switching
            between different Anaconda Repository instances.
            """),
        'no_dependencies': dals("""
            Do not install, update, remove, or change dependencies. This WILL lead to broken
            environments and inconsistent behavior. Use at your own risk.
            """),
        'non_admin_enabled': dals("""
            Allows completion of conda's create, install, update, and remove operations, for
            non-privileged (non-root or non-administrator) users.
            """),
        'notify_outdated_conda': dals("""
            Notify if a newer version of conda is detected during a create, install, update,
            or remove operation.
            """),
        'offline': dals("""
            Restrict conda to cached download content and file:// based urls.
            """),
        'override_channels_enabled': dals("""
            Permit use of the --overide-channels command-line flag.
            """),
        'path_conflict': dals("""
            The method by which conda handle's conflicting/overlapping paths during a
            create, install, or update operation. The value must be one of 'clobber',
            'warn', or 'prevent'. The '--clobber' command-line flag or clobber
            configuration parameter overrides path_conflict set to 'prevent'.
            """),
        'pinned_packages': dals("""
            A list of package specs to pin for every environment resolution.
            This parameter is in BETA, and its behavior may change in a future release.
            """),
        'pkgs_dirs': dals("""
            The list of directories where locally-available packages are linked from at
            install time. Packages not locally available are downloaded and extracted
            into the first writable directory.
            """),
        'proxy_servers': dals("""
            A mapping to enable proxy settings. Keys can be either (1) a scheme://hostname
            form, which will match any request to the given scheme and exact hostname, or
            (2) just a scheme, which will match requests to that scheme. Values are are
            the actual proxy server, and are of the form
            'scheme://[user:password@]host[:port]'. The optional 'user:password' inclusion
            enables HTTP Basic Auth with your proxy.
            """),
        'quiet': dals("""
            Disable progress bar display and other output.
            """),
        'remote_connect_timeout_secs': dals("""
            The number seconds conda will wait for your client to establish a connection
            to a remote url resource.
            """),
        'remote_max_retries': dals("""
            The maximum number of retries each HTTP connection should attempt.
            """),
        'remote_read_timeout_secs': dals("""
            Once conda has connected to a remote resource and sent an HTTP request, the
            read timeout is the number of seconds conda will wait for the server to send
            a response.
            """),
        'report_errors': dals("""
            Opt in, or opt out, of automatic error reporting to core maintainers. Error
            reports are anonymous, with only the error stack trace and information given
            by `conda info` being sent.
            """),
        'rollback_enabled': dals("""
            Should any error occur during an unlink/link transaction, revert any disk
            mutations made to that point in the transaction.
            """),
        'safety_checks': dals("""
            Enforce available safety guarantees during package installation.
            The value must be one of 'enabled', 'warn', or 'disabled'.
            """),
        'shortcuts': dals("""
            Allow packages to create OS-specific shortcuts (e.g. in the Windows Start
            Menu) at install time.
            """),
        'show_channel_urls': dals("""
            Show channel URLs when displaying what is going to be downloaded.
            """),
        'ssl_verify': dals("""
            Conda verifies SSL certificates for HTTPS requests, just like a web
            browser. By default, SSL verification is enabled, and conda operations will
            fail if a required url's certificate cannot be verified. Setting ssl_verify to
            False disables certification verificaiton. The value for ssl_verify can also
            be (1) a path to a CA bundle file, or (2) a path to a directory containing
            certificates of trusted CA.
            """),
        'track_features': dals("""
            A list of features that are tracked by default. An entry here is similar to
            adding an entry to the create_default_packages list.
            """),
        'use_index_cache': dals("""
            Use cache of channel index files, even if it has expired.
            """),
        'use_pip': dals("""
            Include non-conda-installed python packages with conda list. This does not
            affect any conda command or functionality other than the output of the
            command conda list.
            """),
        'verbosity': dals("""
            Sets output log level. 0 is warn. 1 is info. 2 is debug. 3 is trace.
            """),
        'whitelist_channels': dals("""
            The exclusive list of channels allowed to be used on the system. Use of any
            other channels will result in an error. If conda-build channels are to be
            allowed, along with the --use-local command line flag, be sure to include the
            'local' channel in the list. If the list is empty or left undefined, no
            channel exclusions will be enforced.
            """)
    })