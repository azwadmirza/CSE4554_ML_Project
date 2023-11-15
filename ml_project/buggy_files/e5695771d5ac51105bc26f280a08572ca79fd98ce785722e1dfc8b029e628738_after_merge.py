    def _mixin_setup(self):
        salt.utils.warn_until(
            'Nitrogen',
            'Please stop sub-classing PidfileMix and instead subclass '
            'DaemonMixIn which contains the same behavior. PidfileMixin '
            'will be supported until Salt {version}.'
        )
        try:
            self.add_option(
                '--pid-file', dest='pidfile',
                default=os.path.join(
                    syspaths.PIDFILE_DIR, '{0}.pid'.format(self.get_prog_name())
                ),
                help=('Specify the location of the pidfile. Default: %default')
            )

            # Since there was no colision with DaemonMixin, let's add the
            # pidfile mixin methods. This is used using types.MethodType
            # because if we had defined these at the class level, they would
            # have overridden the exact same methods from the DaemonMixin.

            def set_pidfile(self):
                from salt.utils.process import set_pidfile
                set_pidfile(self.config['pidfile'], self.config['user'])

            self.set_pidfile = types.MethodType(set_pidfile, self)

            def check_pidfile(self):
                '''
                Report whether a pidfile exists
                '''
                from salt.utils.process import check_pidfile
                return check_pidfile(self.config['pidfile'])

            self.check_pidfile = types.MethodType(check_pidfile, self)

            def get_pidfile(self):
                '''
                Return a pid contained in a pidfile
                '''
                from salt.utils.process import get_pidfile
                return get_pidfile(self.config['pidfile'])

            self.get_pidfile = types.MethodType(get_pidfile, self)
        except optparse.OptionConflictError:
            # The option was already added by the DaemonMixin
            pass