    def _mixin_setup(self):
        salt.utils.warn_until(
            'Nitrogen',
            'Please stop sub-classing PidfileMix and instead subclass '
            'DaemonMixIn which contains the same behavior. PidfileMixin '
            'will be supported until Salt {version}.'
        )
        self.add_option(
            '--pid-file', dest='pidfile',
            default=os.path.join(
                syspaths.PIDFILE_DIR, '{0}.pid'.format(self.get_prog_name())
            ),
            help=('Specify the location of the pidfile. Default: %default')
        )