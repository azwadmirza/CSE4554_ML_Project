    def run(self):
        """Run the ansible command

        Subclasses must implement this method.  It does the actual work of
        running an Ansible command.
        """

        display.vv(to_text(self.parser.get_version()))

        if C.CONFIG_FILE:
            display.v(u"Using %s as config file" % to_text(C.CONFIG_FILE))
        else:
            display.v(u"No config file found; using defaults")

        # warn about deprecated config options
        for deprecated in C.config.DEPRECATED:
            name = deprecated[0]
            why = deprecated[1]['why']
            if 'alternatives' in deprecated[1]:
                alt = ', use %s instead' % deprecated[1]['alternatives']
            else:
                alt = ''
            ver = deprecated[1]['version']
            display.deprecated("%s option, %s %s" % (name, why, alt), version=ver)

        # Errors with configuration entries
        if C.config.UNABLE:
            for unable in C.config.UNABLE:
                display.error("Unable to set correct type for configuration entry for %s: %s" % (unable, C.config.UNABLE[unable]))
            raise AnsibleError("Invalid configuration settings")