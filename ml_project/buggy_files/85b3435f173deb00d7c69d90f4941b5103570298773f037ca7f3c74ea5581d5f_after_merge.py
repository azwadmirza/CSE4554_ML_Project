    def send_cgroup_telemetry(self):
        if self.last_cgroup_telemetry is None:
            self.last_cgroup_telemetry = datetime.datetime.utcnow()

        if datetime.datetime.utcnow() >= (self.last_telemetry_heartbeat + MonitorHandler.CGROUP_TELEMETRY_PERIOD):
            try:
                for cgroup_name, metrics in CGroupsTelemetry.collect_all_tracked().items():
                    for metric_group, metric_name, value in metrics:
                        if value > 0:
                            report_metric(metric_group, metric_name, cgroup_name, value)
            except Exception as e:
                logger.warn("Monitor: failed to collect cgroups performance metrics: {0}", ustr(e))
                logger.verbose(traceback.format_exc())

            # Look for extension cgroups we're not already tracking and track them
            try:
                CGroupsTelemetry.update_tracked(self.protocol.client.get_current_handlers())
            except Exception as e:
                logger.warn("Monitor: failed to update cgroups tracked extensions: {0}", ustr(e))
                logger.verbose(traceback.format_exc())

            self.last_cgroup_telemetry = datetime.datetime.utcnow()