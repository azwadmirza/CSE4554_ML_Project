    def __init__(self,
                 host,
                 port,
                 redis_address,
                 redis_password=None,
                 log_dir=None):
        self.dashboard_head = dashboard_head.DashboardHead(
            http_host=host,
            http_port=port,
            redis_address=redis_address,
            redis_password=redis_password,
            log_dir=log_dir)

        # Setup Dashboard Routes
        build_dir = setup_static_dir()
        logger.info("Setup static dir for dashboard: %s", build_dir)
        dashboard_utils.ClassMethodRouteTable.bind(self)