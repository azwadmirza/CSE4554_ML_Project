    def render_GET(self, request):
        """
        .. http:get:: /debug/memory/history

        A GET request to this endpoint returns information about memory usage history in the form of a list.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/debug/memory/history

            **Example response**:

            .. sourcecode:: javascript

                {
                    "memory_history": [{
                        "time": 1504015291214,
                        "mem": 324324,
                    }, ...]
                }
        """
        return json.dumps({"memory_history": self.session.lm.resource_monitor.get_memory_history_dict()})