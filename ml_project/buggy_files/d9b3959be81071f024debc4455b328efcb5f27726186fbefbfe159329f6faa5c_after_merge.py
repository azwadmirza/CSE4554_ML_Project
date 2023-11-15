    def setup_dependent_package(self, module, dependent_spec):
        """Called before perl modules' install() methods.
           In most cases, extensions will only need to have one line:
           perl('Makefile.PL','INSTALL_BASE=%s' % self.prefix)
        """

        # If system perl is used through packages.yaml
        # there cannot be extensions.
        if dependent_spec.package.is_extension:

            # perl extension builds can have a global perl
            # executable function
            module.perl = self.spec['perl'].command

            # Add variables for library directory
            module.perl_lib_dir = dependent_spec.prefix.lib.perl5

            # Make the site packages directory for extensions,
            # if it does not exist already.
            mkdirp(module.perl_lib_dir)