def migrate(config_file, current_version, target_version, out=print, i=input):
    logger = logging.getLogger(__name__)
    if current_version < Config.EARLIEST_SUPPORTED_VERSION:
        raise ConfigError("The config file in {} is too old. Please delete it and reconfigure Rally from scratch with {} configure."
                          .format(config_file.location, PROGRAM_NAME))

    prompter = Prompter(i=i, o=out, assume_defaults=False)
    logger.info("Upgrading configuration from version [%s] to [%s].", current_version, target_version)
    # Something is really fishy. We don't want to downgrade the configuration.
    if current_version >= target_version:
        raise ConfigError("The existing config file is available in a later version already. Expected version <= [%s] but found [%s]"
                          % (target_version, current_version))
    # but first a backup...
    config_file.backup()
    config = config_file.load(interpolation=None)

    if current_version == 12 and target_version > current_version:
        # the current configuration allows to benchmark from sources
        if "build" in config and "gradle.bin" in config["build"]:
            java_9_home = io.guess_java_home(major_version=9)
            from esrally.utils import jvm
            if java_9_home and not jvm.is_early_access_release(java_9_home):
                logger.debug("Autodetected a JDK 9 installation at [%s]", java_9_home)
                if "runtime" not in config:
                    config["runtime"] = {}
                config["runtime"]["java9.home"] = java_9_home
            else:
                logger.debug("Could not autodetect a JDK 9 installation. Checking [java.home] already points to a JDK 9.")
                detected = False
                if "runtime" in config:
                    java_home = config["runtime"]["java.home"]
                    if jvm.major_version(java_home) == 9 and not jvm.is_early_access_release(java_home):
                        config["runtime"]["java9.home"] = java_home
                        detected = True

                if not detected:
                    logger.debug("Could not autodetect a JDK 9 installation. Asking user.")
                    raw_java_9_home = prompter.ask_property("Enter the JDK 9 root directory", check_path_exists=True, mandatory=False)
                    if raw_java_9_home and jvm.major_version(raw_java_9_home) == 9 and not jvm.is_early_access_release(raw_java_9_home):
                        java_9_home = io.normalize_path(raw_java_9_home) if raw_java_9_home else None
                        config["runtime"]["java9.home"] = java_9_home
                    else:
                        out("********************************************************************************")
                        out("You don't have a valid JDK 9 installation and cannot benchmark source builds.")
                        out("")
                        out("You can still benchmark binary distributions with e.g.:")
                        out("")
                        out("  %s --distribution-version=6.0.0" % PROGRAM_NAME)
                        out("********************************************************************************")
                        out("")

        current_version = 13
        config["meta"]["config.version"] = str(current_version)

    if current_version == 13 and target_version > current_version:
        # This version replaced java9.home with java10.home
        if "build" in config and "gradle.bin" in config["build"]:
            java_10_home = io.guess_java_home(major_version=10)
            from esrally.utils import jvm
            if java_10_home and not jvm.is_early_access_release(java_10_home):
                logger.debug("Autodetected a JDK 10 installation at [%s]", java_10_home)
                if "runtime" not in config:
                    config["runtime"] = {}
                config["runtime"]["java10.home"] = java_10_home
            else:
                logger.debug("Could not autodetect a JDK 10 installation. Checking [java.home] already points to a JDK 10.")
                detected = False
                if "runtime" in config:
                    java_home = config["runtime"]["java.home"]
                    if jvm.major_version(java_home) == 10 and not jvm.is_early_access_release(java_home):
                        config["runtime"]["java10.home"] = java_home
                        detected = True

                if not detected:
                    logger.debug("Could not autodetect a JDK 10 installation. Asking user.")
                    raw_java_10_home = prompter.ask_property("Enter the JDK 10 root directory", check_path_exists=True, mandatory=False)
                    if raw_java_10_home and jvm.major_version(raw_java_10_home) == 10 and not jvm.is_early_access_release(raw_java_10_home):
                        java_10_home = io.normalize_path(raw_java_10_home) if raw_java_10_home else None
                        config["runtime"]["java10.home"] = java_10_home
                    else:
                        out("********************************************************************************")
                        out("You don't have a valid JDK 10 installation and cannot benchmark source builds.")
                        out("")
                        out("You can still benchmark binary distributions with e.g.:")
                        out("")
                        out("  %s --distribution-version=6.0.0" % PROGRAM_NAME)
                        out("********************************************************************************")
                        out("")

        current_version = 14
        config["meta"]["config.version"] = str(current_version)

    if current_version == 14 and target_version > current_version:
        # Be agnostic about build tools. Let use specify build commands for plugins and elasticsearch
        # but also use gradlew by default for Elasticsearch and Core plugin builds, if nothing else has been specified.

        def warn_if_plugin_build_task_is_in_use(config):
            if "source" not in config:
                return
            for k, v in config["source"].items():
                plugin_match = re.match('^plugin\.([^.]+)\.build\.task$',k)
                if plugin_match != None and len(plugin_match.groups()) > 0 :
                    plugin_name = plugin_match.group(1)
                    new_key = "plugin.{}.build.command".format(plugin_name)
                    out("\n"
                        "WARNING:"
                        "  The build.task property for plugins has been obsoleted in favor of the full build.command."
                        "  You will need to edit the plugin [{}] section in {} and change from:"
                        "  [{} = {}] to [{} = <the full command>]."
                        "  Please refer to the documentation for more details:"
                        "  {}.\n".format(plugin_match.group(1), config_file.location, k, v, new_key,
                                         console.format.link("%selasticsearch_plugins.html#running-a-benchmark-with-plugins" % DOC_LINK)))

        if "build" in config:
            logger.info("Removing Gradle configuration as Rally now uses the Gradle Wrapper to build Elasticsearch.")
            config.pop("build", None)
        warn_if_plugin_build_task_is_in_use(config)

        current_version = 15
        config["meta"]["config.version"] = str(current_version)

    if current_version == 15 and target_version > current_version:
        if "distributions" in config:
            # Remove obsolete settings
            config["distributions"].pop("release.1.url", None)
            config["distributions"].pop("release.2.url", None)
            config["distributions"].pop("release.url", None)
        current_version = 16
        config["meta"]["config.version"] = str(current_version)

    if current_version == 16 and target_version > current_version:
        config.pop("runtime", None)
        current_version = 17
        config["meta"]["config.version"] = str(current_version)

    # all migrations done
    config_file.store(config)
    logger.info("Successfully self-upgraded configuration to version [%s]", target_version)