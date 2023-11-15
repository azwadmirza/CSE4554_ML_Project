    def _split_routing_response(data, service):
        """
        Splits the routing responses per data center for the federator output.

        Returns a dictionary with the keys being the root URLs of the fdsnws
        endpoints and the values the data payloads for that endpoint.

        :param data: The return value from the EIDAWS routing service.
        """
        if service.lower() == "dataselect":
            key = "DATASELECTSERVICE"
        elif service.lower() == "station":
            key = "STATIONSERVICE"
        else:
            raise ValueError("Service must be 'dataselect' or 'station'.")

        split = collections.defaultdict(list)
        current_key = None
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            if "http://" in line:
                if key not in line:
                    continue
                current_key = line[len(key) + 1:line.find("/fdsnws")]
                continue
            # Anything before the first data center can be ignored.
            if current_key is None:
                continue
            split[current_key].append(line)

        return {k: "\n".join(v) for k, v in split.items()}