    def process_saltfile(self):
        if self.options.saltfile is None:
            # No one passed a Saltfile as an option, environment variable!?
            self.options.saltfile = os.environ.get('SALT_SALTFILE', None)

        if self.options.saltfile is None:
            # If we're here, no one passed a Saltfile either to the CLI tool or
            # as an environment variable.
            # Is there a Saltfile in the current directory?
            try:  # cwd may not exist if it was removed but salt was run from it
                saltfile = os.path.join(os.getcwd(), 'Saltfile')
            except OSError:
                saltfile = ''
            if os.path.isfile(saltfile):
                self.options.saltfile = saltfile
        else:
            saltfile = self.options.saltfile

        if not self.options.saltfile:
            # There's still no valid Saltfile? No need to continue...
            return

        if not os.path.isfile(self.options.saltfile):
            self.error(
                '{0!r} file does not exist.\n'.format(self.options.saltfile
                )
            )

        # Make sure we have an absolute path
        self.options.saltfile = os.path.abspath(self.options.saltfile)

        # Make sure we let the user know that we will be loading a Saltfile
        logging.getLogger(__name__).info(
            'Loading Saltfile from {0!r}'.format(self.options.saltfile)
        )

        saltfile_config = config._read_conf_file(saltfile)

        if not saltfile_config:
            # No configuration was loaded from the Saltfile
            return

        if self.get_prog_name() not in saltfile_config:
            # There's no configuration specific to the CLI tool. Stop!
            return

        # We just want our own configuration
        cli_config = saltfile_config[self.get_prog_name()]

        # If there are any options, who's names match any key from the loaded
        # Saltfile, we need to update its default value
        for option in self.option_list:
            if option.dest is None:
                # --version does not have dest attribute set for example.
                continue

            if option.dest not in cli_config:
                # If we don't have anything in Saltfile for this option, let's
                # continue processing right now
                continue

            # Get the passed value from shell. If empty get the default one
            default = self.defaults.get(option.dest)
            value = getattr(self.options, option.dest, default)
            if value != default:
                # The user passed an argument, we won't override it with the
                # one from Saltfile, if any
                continue

            # We reached this far! Set the Saltfile value on the option
            setattr(self.options, option.dest, cli_config[option.dest])

        # Let's also search for options referred in any option groups
        for group in self.option_groups:
            for option in group.option_list:
                if option.dest is None:
                    continue

                if option.dest not in cli_config:
                    # If we don't have anything in Saltfile for this option,
                    # let's continue processing right now
                    continue

                # Get the passed value from shell. If empty get the default one
                default = self.defaults.get(option.dest)
                value = getattr(self.options, option.dest, default)
                if value != default:
                    # The user passed an argument, we won't override it with
                    # the one from Saltfile, if any
                    continue

                if option.dest in cli_config:
                    setattr(self.options,
                            option.dest,
                            cli_config[option.dest])

        # Any left over value in the saltfile can now be safely added
        for key in cli_config:
            setattr(self.options, key, cli_config[key])