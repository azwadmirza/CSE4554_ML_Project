    def check_rest_availability(self, initiator, responder):
        response = self.client.post(node_or_sprout=responder,
                                    data=bytes(initiator),
                                    path="ping",
                                    timeout=6,  # Two round trips are expected
                                    )
        return response