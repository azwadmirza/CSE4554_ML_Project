    def init_cgroups():
        # Track metrics for the roll-up cgroup and for the agent cgroup
        try:
            CGroupsTelemetry.track_cgroup(CGroups.for_extension(""))
            CGroupsTelemetry.track_agent()
        except Exception as e:
            logger.error("monitor: Exception tracking wrapper and agent: {0} [{1}]", e, traceback.format_exc())