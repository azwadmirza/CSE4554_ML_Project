    def create_config(self, config_file, advanced_config=False, assume_defaults=False):
        """
        Either creates a new configuration file or overwrites an existing one. Will ask the user for input on configurable properties
        and writes them to the configuration file in ~/.rally/rally.ini.

        :param config_file:
        :param advanced_config: Whether to ask for properties that are not necessary for everyday use (on a dev machine). Default: False.
        :param assume_defaults: If True, assume the user accepted all values for which defaults are provided. Mainly intended for automatic
        configuration in CI run. Default: False.
        """
        self.prompter = Prompter(self.i, self.sec_i, self.o, assume_defaults)

        if advanced_config:
            self.o("Running advanced configuration. You can get additional help at:")
            self.o("")
            self.o("  %s" % console.format.link("%sconfiguration.html" % DOC_LINK))
            self.o("")
        else:
            self.o("Running simple configuration. Run the advanced configuration with:")
            self.o("")
            self.o("  %s configure --advanced-config" % PROGRAM_NAME)
            self.o("")

        if config_file.present:
            self.o("\nWARNING: Will overwrite existing config file at [%s]\n" % config_file.location)
            self.logger.debug("Detected an existing configuration file at [%s]", config_file.location)
        else:
            self.logger.debug("Did not detect a configuration file at [%s]. Running initial configuration routine.", config_file.location)

        root_dir = io.normalize_path(os.path.abspath(os.path.join(config_file.config_dir, "benchmarks")))
        if advanced_config:
            root_dir = io.normalize_path(self._ask_property("Enter the benchmark data directory", default_value=root_dir))
        else:
            self.o("* Setting up benchmark data directory in %s" % root_dir)

        # We try to autodetect an existing ES source directory
        guess = self._guess_es_src_dir()
        if guess:
            source_dir = guess
            self.logger.debug("Autodetected Elasticsearch project directory at [%s].", source_dir)
        else:
            default_src_dir = os.path.join(root_dir, "src", "elasticsearch")
            self.logger.debug("Could not autodetect Elasticsearch project directory. Providing [%s] as default.", default_src_dir)
            source_dir = default_src_dir

        if advanced_config:
            source_dir = io.normalize_path(self._ask_property("Enter your Elasticsearch project directory:",
                                                              default_value=source_dir))
        if not advanced_config:
            self.o("* Setting up benchmark source directory in %s" % source_dir)
            self.o("")

        # Not everybody might have SSH access. Play safe with the default. It may be slower but this will work for everybody.
        repo_url = "https://github.com/elastic/elasticsearch.git"

        if advanced_config:
            data_store_choice = self._ask_property("Where should metrics be kept?"
                                                   "\n\n"
                                                   "(1) In memory (simpler but less options for analysis)\n"
                                                   "(2) Elasticsearch (requires a separate ES instance, keeps all raw samples for analysis)"
                                                   "\n\n", default_value="1", choices=["1", "2"])
            if data_store_choice == "1":
                env_name = "local"
                data_store_type = "in-memory"
                data_store_host, data_store_port, data_store_secure, data_store_user, data_store_password = "", "", "", "", ""
            else:
                data_store_type = "elasticsearch"
                data_store_host, data_store_port, data_store_secure, data_store_user, data_store_password = self._ask_data_store()

                env_name = self._ask_env_name()

            preserve_install = convert.to_bool(self._ask_property("Do you want Rally to keep the Elasticsearch benchmark candidate "
                                                                  "installation including the index (will use several GB per trial run)?",
                                                                  default_value=False))
        else:
            # Does not matter for an in-memory store
            env_name = "local"
            data_store_type = "in-memory"
            data_store_host, data_store_port, data_store_secure, data_store_user, data_store_password = "", "", "", "", ""
            preserve_install = False

        config = configparser.ConfigParser()
        config["meta"] = {}
        config["meta"]["config.version"] = str(Config.CURRENT_CONFIG_VERSION)

        config["system"] = {}
        config["system"]["env.name"] = env_name

        config["node"] = {}
        config["node"]["root.dir"] = root_dir

        final_source_dir = io.normalize_path(os.path.abspath(os.path.join(source_dir, os.pardir)))
        config["node"]["src.root.dir"] = final_source_dir

        config["source"] = {}
        config["source"]["remote.repo.url"] = repo_url
        # the Elasticsearch directory is just the last path component (relative to the source root directory)
        config["source"]["elasticsearch.src.subdir"] = io.basename(source_dir)

        config["benchmarks"] = {}
        config["benchmarks"]["local.dataset.cache"] = os.path.join(root_dir, "data")

        config["reporting"] = {}
        config["reporting"]["datastore.type"] = data_store_type
        config["reporting"]["datastore.host"] = data_store_host
        config["reporting"]["datastore.port"] = data_store_port
        config["reporting"]["datastore.secure"] = data_store_secure
        config["reporting"]["datastore.user"] = data_store_user
        config["reporting"]["datastore.password"] = data_store_password

        config["tracks"] = {}
        config["tracks"]["default.url"] = "https://github.com/elastic/rally-tracks"

        config["teams"] = {}
        config["teams"]["default.url"] = "https://github.com/elastic/rally-teams"

        config["defaults"] = {}
        config["defaults"]["preserve_benchmark_candidate"] = str(preserve_install)

        config["distributions"] = {}
        config["distributions"]["release.cache"] = "true"

        config_file.store(config)

        self.o("Configuration successfully written to %s. Happy benchmarking!" % config_file.location)
        self.o("")
        self.o("More info about Rally:")
        self.o("")
        self.o("* Type %s --help" % PROGRAM_NAME)
        self.o("* Read the documentation at %s" % console.format.link(DOC_LINK))
        self.o("* Ask a question on the forum at %s" % console.format.link("https://discuss.elastic.co/c/elasticsearch/rally"))