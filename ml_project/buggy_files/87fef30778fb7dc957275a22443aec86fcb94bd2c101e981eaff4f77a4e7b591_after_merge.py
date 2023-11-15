    def render_GET(self, request):
        """
        .. http:get:: /debug/cpu/history

        A GET request to this endpoint returns information about CPU usage history in the form of a list.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/debug/cpu/history

            **Example response**:

            .. sourcecode:: javascript

                {
                    "cpu_history": [{
                        "time": 1504015291214,
                        "cpu": 3.4,
                    }, ...]
                }
        """
        history = self.session.lm.resource_monitor.get_cpu_history_dict() if self.session.lm.resource_monitor else {}
        return json.dumps({"cpu_history": history})