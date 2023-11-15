    def __init__(self, name, *args, **kwargs):
        # If the user provided `--name perl-cpp`, don't rename it perl-perl-cpp
        if not name.startswith('perl-'):
            # Make it more obvious that we are renaming the package
            tty.msg("Changing package name from {0} to perl-{0}".format(name))
            name = 'perl-{0}'.format(name)

        super(PerlmakePackageTemplate, self).__init__(name, *args, **kwargs)