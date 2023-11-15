    def render_GET(self, request):
        """
        .. http:get:: /debug/profiler

        A GET request to this endpoint returns information about the state of the profiler.
        This state is either STARTED or STOPPED.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/debug/profiler

            **Example response**:

            .. sourcecode:: javascript

                {
                    "state": "STARTED"
                }
        """
        monitor_enabled = self.session.config.get_resource_monitor_enabled()
        state = "STARTED" if (monitor_enabled and self.session.lm.resource_monitor.profiler_running) else "STOPPED"
        return json.dumps({"state": state})