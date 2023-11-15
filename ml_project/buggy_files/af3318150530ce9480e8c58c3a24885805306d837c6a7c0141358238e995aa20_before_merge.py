    def check_rest_availability(self, requesting_ursula, responding_ursula, certificate_filepath=None):
        response = self.client.post(node_or_sprout=responding_ursula,
                                    data=bytes(requesting_ursula),
                                    path="ping",
                                    timeout=4,  # Two round trips are expected
                                    certificate_filepath=certificate_filepath)
        return response