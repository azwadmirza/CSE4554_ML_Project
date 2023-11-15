    def datagram_received(self, data, addr) -> None:
        """DNS response packet received."""
        log_binary(
            _LOGGER,
            f"Received DNS response from {addr}",
            level=TRAFFIC_LEVEL,
            Data=data,
        )

        # Suppress decode errors for now (but still log)
        try:
            services = parse_services(DnsMessage().unpack(data))
        except UnicodeDecodeError:
            log_binary(_LOGGER, "Failed to decode message", Msg=data)
            return

        # Ignore responses from other services
        for service in services:
            if (
                service.type not in self.services
                and service.type != DEVICE_INFO_SERVICE
            ):
                return

        is_sleep_proxy = all(service.port == 0 for service in services)
        if is_sleep_proxy:
            self._unicasts[addr[0]] = create_request(
                [service.name + "." + service.type for service in services],
                qtype=QTYPE_ANY,
            )
        else:
            response = Response(
                services=services,
                deep_sleep=(addr[0] in self._unicasts),
                model=_get_model(services),
            )

            if self.end_condition(response):
                # Matches end condition: replace everything found so far and abort
                self.responses = {IPv4Address(addr[0]): response}
                self.semaphore.release()
                self.close()
            else:
                self.responses[IPv4Address(addr[0])] = response