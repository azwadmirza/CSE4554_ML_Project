    def add_parser_arguments(cls, add):
        add("enmod", default=constants.os_constant("enmod"),
            help="Path to the Apache 'a2enmod' binary.")
        add("dismod", default=constants.os_constant("dismod"),
            help="Path to the Apache 'a2dismod' binary.")
        add("le-vhost-ext", default=constants.os_constant("le_vhost_ext"),
            help="SSL vhost configuration extension.")
        add("server-root", default=constants.os_constant("server_root"),
            help="Apache server root directory.")
        add("vhost-root", default=None,
            help="Apache server VirtualHost configuration root")
        add("logs-root", default=constants.os_constant("logs_root"),
            help="Apache server logs directory")
        add("challenge-location",
            default=constants.os_constant("challenge_location"),
            help="Directory path for challenge configuration.")
        add("handle-modules", default=constants.os_constant("handle_mods"),
            help="Let installer handle enabling required modules for you." +
                 "(Only Ubuntu/Debian currently)")
        add("handle-sites", default=constants.os_constant("handle_sites"),
            help="Let installer handle enabling sites for you." +
                 "(Only Ubuntu/Debian currently)")
        util.add_deprecated_argument(add, argument_name="ctl", nargs=1)
        util.add_deprecated_argument(
            add, argument_name="init-script", nargs=1)