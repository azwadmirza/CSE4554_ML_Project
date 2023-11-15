    def __init__(self, aug, root, vhostroot=None, version=(2, 4),
                 configurator=None):
        # Note: Order is important here.

        # Needed for calling save() with reverter functionality that resides in
        # AugeasConfigurator superclass of ApacheConfigurator. This resolves
        # issues with aug.load() after adding new files / defines to parse tree
        self.configurator = configurator

        # This uses the binary, so it can be done first.
        # https://httpd.apache.org/docs/2.4/mod/core.html#define
        # https://httpd.apache.org/docs/2.4/mod/core.html#ifdefine
        # This only handles invocation parameters and Define directives!
        self.parser_paths = {}
        self.variables = {}
        if version >= (2, 4):
            self.update_runtime_variables()

        self.aug = aug
        # Find configuration root and make sure augeas can parse it.
        self.root = os.path.abspath(root)
        self.loc = {"root": self._find_config_root()}
        self.parse_file(self.loc["root"])

        # This problem has been fixed in Augeas 1.0
        self.standardize_excl()

        # Temporarily set modules to be empty, so that find_dirs can work
        # https://httpd.apache.org/docs/2.4/mod/core.html#ifmodule
        # This needs to come before locations are set.
        self.modules = set()
        self.init_modules()

        # Set up rest of locations
        self.loc.update(self._set_locations())

        self.existing_paths = copy.deepcopy(self.parser_paths)

        # Must also attempt to parse additional virtual host root
        if vhostroot:
            self.parse_file(os.path.abspath(vhostroot) + "/" +
                            constants.os_constant("vhost_files"))

        # check to see if there were unparsed define statements
        if version < (2, 4):
            if self.find_dir("Define", exclude=False):
                raise errors.PluginError("Error parsing runtime variables")