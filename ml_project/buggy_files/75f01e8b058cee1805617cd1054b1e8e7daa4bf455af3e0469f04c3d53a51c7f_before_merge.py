    def __init__(self, aug, root, vhostroot, version=(2, 4)):
        # Note: Order is important here.

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
        self._parse_file(self.loc["root"])

        self.vhostroot = os.path.abspath(vhostroot)

        # This problem has been fixed in Augeas 1.0
        self.standardize_excl()

        # Temporarily set modules to be empty, so that find_dirs can work
        # https://httpd.apache.org/docs/2.4/mod/core.html#ifmodule
        # This needs to come before locations are set.
        self.modules = set()
        self.init_modules()

        # Set up rest of locations
        self.loc.update(self._set_locations())

        # Must also attempt to parse virtual host root
        self._parse_file(self.vhostroot + "/" +
                         constants.os_constant("vhost_files"))

        # check to see if there were unparsed define statements
        if version < (2, 4):
            if self.find_dir("Define", exclude=False):
                raise errors.PluginError("Error parsing runtime variables")