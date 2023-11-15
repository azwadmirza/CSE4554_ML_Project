    def process(self):
        event = self.receive_message()

        keys = ["source.%s", "destination.%s"]

        for key in keys:
            ip_key = key % "ip"

            if not event.contains(ip_key):
                continue

            ip = event.get(ip_key)
            ip_version = IPAddress.version(ip)
            ip_integer = IPAddress.to_int(ip)

            if ip_version == 4:
                minimum = MINIMUM_BGP_PREFIX_IPV4

            elif ip_version == 6:
                minimum = MINIMUM_BGP_PREFIX_IPV6

            else:
                raise ValueError('Unexpected IP version '
                                 '{!r}.'.format(ip_version))

            cache_key = bin(ip_integer)[2: minimum + 2]
            result_json = self.cache.get(cache_key)

            if result_json:
                result = json.loads(result_json)
            else:
                result = Cymru.query(ip)
                result_json = json.dumps(result)
                self.cache.set(cache_key, result_json)

            for result_key, result_value in result.items():
                event.add(key % result_key, result_value, force=True)

        self.send_message(event)
        self.acknowledge_message()