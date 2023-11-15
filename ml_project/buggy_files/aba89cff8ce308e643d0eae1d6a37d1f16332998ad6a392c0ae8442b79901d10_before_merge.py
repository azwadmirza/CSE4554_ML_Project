    def __init__(self, name, *args):
        # If the user provided `--name py-numpy`, don't rename it py-py-numpy
        if not name.startswith('py-'):
            # Make it more obvious that we are renaming the package
            tty.msg("Changing package name from {0} to py-{0}".format(name))
            name = 'py-{0}'.format(name)

        super(PythonPackageTemplate, self).__init__(name, *args)