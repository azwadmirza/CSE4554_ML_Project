    def do_alert(self, alerter: Alerter) -> None:
        """Use the given alerter object to send an alert, if needed."""
        alerter.check_dependencies(self.failed + self.still_failing + self.skipped)
        for (name, this_monitor) in list(self.monitors.items()):
            # Don't generate alerts for monitors which want it done remotely
            if this_monitor.remote_alerting:
                module_logger.debug(
                    "skipping alert for monitor %s as it wants remote alerting", name
                )
                continue
            try:
                if this_monitor.notify:
                    alerter.send_alert(name, this_monitor)
                else:
                    module_logger.warning("monitor %s has notifications disabled", name)
            except Exception:  # pragma: no cover
                module_logger.exception("exception caught while alerting for %s", name)
        for host_monitors in self.remote_monitors.values():
            for (name, monitor) in host_monitors.items():
                try:
                    if monitor.remote_alerting:
                        alerter.send_alert(name, monitor)
                    else:
                        module_logger.debug(
                            "not alerting for monitor %s as it doesn't want remote alerts",
                            name,
                        )
                except Exception:  # pragma: no cover
                    module_logger.exception(
                        "exception caught while alerting for remote monitor %s", name
                    )