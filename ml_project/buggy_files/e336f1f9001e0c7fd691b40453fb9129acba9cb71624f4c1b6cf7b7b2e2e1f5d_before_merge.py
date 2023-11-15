    def __init__(self, name, *args):
        # If the user provided `--name octave-splines`, don't rename it
        # octave-octave-splines
        if not name.startswith('octave-'):
            # Make it more obvious that we are renaming the package
            tty.msg("Changing package name from {0} to octave-{0}".format(name))  # noqa
            name = 'octave-{0}'.format(name)

        super(OctavePackageTemplate, self).__init__(name, *args)