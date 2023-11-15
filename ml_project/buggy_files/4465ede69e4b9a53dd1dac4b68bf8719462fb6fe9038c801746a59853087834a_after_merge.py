    def __init__(self, name, *args, **kwargs):
        # If the user provided `--name py-pyqt4`, don't rename it py-py-pyqt4
        if not name.startswith('py-'):
            # Make it more obvious that we are renaming the package
            tty.msg("Changing package name from {0} to py-{0}".format(name))
            name = 'py-{0}'.format(name)

        super(SIPPackageTemplate, self).__init__(name, *args, **kwargs)