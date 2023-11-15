    def __init__(self,
                 host,
                 port,
                 port_retries,
                 redis_address,
                 redis_password=None,
                 log_dir=None):
        self.dashboard_head = dashboard_head.DashboardHead(
            http_host=host,
            http_port=port,
            http_port_retries=port_retries,
            redis_address=redis_address,
            redis_password=redis_password,
            log_dir=log_dir)

        # Setup Dashboard Routes
        try:
            build_dir = setup_static_dir()
            logger.info("Setup static dir for dashboard: %s", build_dir)
        except FrontendNotFoundError as ex:
            # Not to raise FrontendNotFoundError due to NPM incompatibilities
            # with Windows.
            # Please refer to ci.sh::build_dashboard_front_end()
            if sys.platform in ["win32", "cygwin"]:
                logger.warning(ex)
            else:
                raise ex
        dashboard_utils.ClassMethodRouteTable.bind(self)