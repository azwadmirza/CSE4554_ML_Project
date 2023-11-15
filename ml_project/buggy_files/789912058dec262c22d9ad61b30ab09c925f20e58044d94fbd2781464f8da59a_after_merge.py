    def init_cgroups():
        # Track metrics for the roll-up cgroup and for the agent cgroup
        try:
            CGroupsTelemetry.track_cgroup(CGroups.for_extension(""))
            CGroupsTelemetry.track_agent()
        except Exception as e:
            # when a hierarchy is not mounted, we raise an exception
            # and we should therefore only issue a warning, since this
            # is not unexpected
            logger.warn("Monitor: cgroups not initialized: {0}", ustr(e))
            logger.verbose(traceback.format_exc())