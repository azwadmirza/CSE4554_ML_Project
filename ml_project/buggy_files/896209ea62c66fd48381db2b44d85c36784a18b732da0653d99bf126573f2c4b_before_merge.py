    def _split_routing_response(data):
        """
        Splits the routing responses per data center for the EIDAWS output.

        Returns a dictionary with the keys being the root URLs of the fdsnws
        endpoints and the values the data payloads for that endpoint.

        :param data: The return value from the EIDAWS routing service.
        """
        split = collections.defaultdict(list)
        current_key = None
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            if "http" in line and "fdsnws" in line:
                current_key = line[:line.find("/fdsnws")]
                continue
            split[current_key].append(line)

        return {k: "\n".join(v) for k, v in split.items()}