    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        addr = get_addr_from_info(info)

        if addr not in self.found_devices:
            dev = self.check_and_create_device(info, addr)
            self.found_devices[addr] = dev