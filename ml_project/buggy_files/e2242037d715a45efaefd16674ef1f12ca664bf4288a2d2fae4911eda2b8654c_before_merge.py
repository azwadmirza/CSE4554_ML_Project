    def __init__(self, name, *args):
        # If the user provided `--name r-rcpp`, don't rename it r-r-rcpp
        if not name.startswith('r-'):
            # Make it more obvious that we are renaming the package
            tty.msg("Changing package name from {0} to r-{0}".format(name))
            name = 'r-{0}'.format(name)

        super(RPackageTemplate, self).__init__(name, *args)