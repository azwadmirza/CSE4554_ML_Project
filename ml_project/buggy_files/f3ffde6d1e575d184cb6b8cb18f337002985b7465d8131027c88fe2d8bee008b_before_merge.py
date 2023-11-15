    def _parse_args(self) -> argparse.Namespace:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)

        # Workaround issue in argparse with action='append' and default value
        # (see https://bugs.python.org/issue16399)
        # Allow no-config for certain commands (like downloading / plotting)
        if ('config' in parsed_arg and parsed_arg.config is None and
            ((Path.cwd() / constants.DEFAULT_CONFIG).is_file() or
             not ('command' in parsed_arg and parsed_arg.command in NO_CONF_REQURIED))):
            parsed_arg.config = [constants.DEFAULT_CONFIG]

        return parsed_arg