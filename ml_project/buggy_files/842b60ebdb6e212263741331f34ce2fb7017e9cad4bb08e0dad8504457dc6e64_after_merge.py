    def load_from_powershell(self):
        if not conf.prog.os_access:
            return
        ifaces_ips = None
        for i in get_windows_if_list():
            try:
                interface = NetworkInterface(i)
                self.data[interface.guid] = interface
                # If no IP address was detected using winpcap and if
                # the interface is not the loopback one, look for
                # internal windows interfaces
                if not interface.ip:
                    if not ifaces_ips:  # ifaces_ips is used as a cache
                        ifaces_ips = get_ips()
                    # If it exists, retrieve the interface's IP from the cache
                    interface.ip = ifaces_ips.get(interface.name, "")[0]
            except (KeyError, PcapNameNotFoundError):
                pass

        if not self.data and conf.use_winpcapy:
            _detect = pcap_service_status()

            def _ask_user():
                if not conf.interactive:
                    return False
                while True:
                    _confir = input("Do you want to start it ? (yes/no) [y]: ").lower().strip()  # noqa: E501
                    if _confir in ["yes", "y", ""]:
                        return True
                    elif _confir in ["no", "n"]:
                        return False
                return False
            _error_msg = "No match between your pcap and windows network interfaces found. "  # noqa: E501
            if _detect[0] and not _detect[2] and not (hasattr(self, "restarted_adapter") and self.restarted_adapter):  # noqa: E501
                warning("Scapy has detected that your pcap service is not running !")  # noqa: E501
                if not conf.interactive or _ask_user():
                    succeed = pcap_service_start(askadmin=conf.interactive)
                    self.restarted_adapter = True
                    if succeed:
                        log_loading.info("Pcap service started !")
                        self.load_from_powershell()
                        return
                _error_msg = "Could not start the pcap service ! "
            warning(_error_msg +
                    "You probably won't be able to send packets. "
                    "Deactivating unneeded interfaces and restarting Scapy might help. "  # noqa: E501
                    "Check your winpcap and powershell installation, and access rights.")  # noqa: E501
        else:
            # Loading state: remove invalid interfaces
            self.remove_invalid_ifaces()
            # Replace LOOPBACK_INTERFACE
            try:
                scapy.consts.LOOPBACK_INTERFACE = self.dev_from_name(
                    scapy.consts.LOOPBACK_NAME,
                )
            except ValueError:
                pass