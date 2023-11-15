    def build_option_parser(self, description, version):
        parser = super(OpenIOShell, self).build_option_parser(
            description,
            version)

        parser.add_argument(
            '--oio-ns',
            metavar='<namespace>',
            dest='ns',
            default=utils.env('OIO_NS'),
            help='Namespace name (Env: OIO_NS)',
        )
        parser.add_argument(
            '--oio-account',
            metavar='<account>',
            dest='account_name',
            default=utils.env('OIO_ACCOUNT'),
            help='Account name (Env: OIO_ACCOUNT)'
        )
        parser.add_argument(
            '--oio-proxyd-url',
            metavar='<proxyd url>',
            dest='proxyd_url',
            default=utils.env('OIO_PROXYD_URL'),
            help='Proxyd URL (Env: OIO_PROXYD_URL)'
        )
        parser.add_argument(
            "--admin",
            dest='admin_mode',
            action='store_true',
            help='passing commands into admin mode')

        return clientmanager.build_plugin_option_parser(parser)