    def gather_host_vmnic_facts(self):
        """Gather vmnic facts"""
        hosts_vmnic_facts = {}
        for host in self.hosts:
            host_vmnic_facts = dict(all=[], available=[], used=[], vswitch=dict(), dvswitch=dict())
            host_nw_system = host.configManager.networkSystem
            if host_nw_system:
                nw_config = host_nw_system.networkConfig
                host_vmnic_facts['all'] = [pnic.device for pnic in nw_config.pnic]
                host_vmnic_facts['num_vmnics'] = (
                    len(filter(lambda s: s.startswith('vmnic'), [pnic.device for pnic in nw_config.pnic]))
                )
                host_vmnic_facts['vmnic_details'] = []
                for pnic in host.config.network.pnic:
                    pnic_facts = dict()
                    if pnic.device.startswith('vmnic'):
                        if pnic.pci:
                            pnic_facts['location'] = pnic.pci
                            for pci_device in host.hardware.pciDevice:
                                if pci_device.id == pnic.pci:
                                    pnic_facts['adapter'] = pci_device.vendorName + ' ' + pci_device.deviceName
                                    break
                        else:
                            pnic_facts['location'] = 'PCI'
                        pnic_facts['device'] = pnic.device
                        pnic_facts['driver'] = pnic.driver
                        if pnic.linkSpeed:
                            pnic_facts['status'] = 'Connected'
                            pnic_facts['actual_speed'] = pnic.linkSpeed.speedMb
                            pnic_facts['actual_duplex'] = 'Full Duplex' if pnic.linkSpeed.duplex else 'Half Duplex'
                        else:
                            pnic_facts['status'] = 'Disconnected'
                            pnic_facts['actual_speed'] = 'N/A'
                            pnic_facts['actual_duplex'] = 'N/A'
                        if pnic.spec.linkSpeed:
                            pnic_facts['configured_speed'] = pnic.spec.linkSpeed.speedMb
                            pnic_facts['configured_duplex'] = 'Full Duplex' if pnic.spec.linkSpeed.duplex else 'Half Duplex'
                        else:
                            pnic_facts['configured_speed'] = 'Auto negotiate'
                            pnic_facts['configured_duplex'] = 'Auto negotiate'
                        pnic_facts['mac'] = pnic.mac
                        # General NIC capabilities
                        if self.capabilities:
                            pnic_facts['nioc_status'] = 'Allowed' if pnic.resourcePoolSchedulerAllowed else 'Not allowed'
                            pnic_facts['auto_negotiation_supported'] = pnic.autoNegotiateSupported
                            pnic_facts['wake_on_lan_supported'] = pnic.wakeOnLanSupported
                        # DirectPath I/O and SR-IOV capabilities and configuration
                        if self.directpath_io:
                            pnic_facts['directpath_io_supported'] = pnic.vmDirectPathGen2Supported
                        if self.directpath_io or self.sriov:
                            if pnic.pci:
                                for pci_device in host.configManager.pciPassthruSystem.pciPassthruInfo:
                                    if pci_device.id == pnic.pci:
                                        if self.directpath_io:
                                            pnic_facts['passthru_enabled'] = pci_device.passthruEnabled
                                            pnic_facts['passthru_capable'] = pci_device.passthruCapable
                                            pnic_facts['passthru_active'] = pci_device.passthruActive
                                        if self.sriov:
                                            try:
                                                if pci_device.sriovCapable:
                                                    pnic_facts['sriov_status'] = (
                                                        'Enabled' if pci_device.sriovEnabled else 'Disabled'
                                                    )
                                                    pnic_facts['sriov_active'] = \
                                                        pci_device.sriovActive
                                                    pnic_facts['sriov_virt_functions'] = \
                                                        pci_device.numVirtualFunction
                                                    pnic_facts['sriov_virt_functions_requested'] = \
                                                        pci_device.numVirtualFunctionRequested
                                                    pnic_facts['sriov_virt_functions_supported'] = \
                                                        pci_device.maxVirtualFunctionSupported
                                                else:
                                                    pnic_facts['sriov_status'] = 'Not supported'
                                            except AttributeError:
                                                pnic_facts['sriov_status'] = 'Not supported'
                        host_vmnic_facts['vmnic_details'].append(pnic_facts)

                vswitch_vmnics = []
                proxy_switch_vmnics = []
                if nw_config.vswitch:
                    for vswitch in nw_config.vswitch:
                        host_vmnic_facts['vswitch'][vswitch.name] = []
                        # Workaround for "AttributeError: 'NoneType' object has no attribute 'nicDevice'"
                        # this issue doesn't happen every time; vswitch.spec.bridge.nicDevice exists!
                        try:
                            for vnic in vswitch.spec.bridge.nicDevice:
                                vswitch_vmnics.append(vnic)
                                host_vmnic_facts['vswitch'][vswitch.name].append(vnic)
                        except AttributeError:
                            pass

                if nw_config.proxySwitch:
                    for proxy_config in nw_config.proxySwitch:
                        dvs_obj = self.find_dvs_by_uuid(uuid=proxy_config.uuid)
                        if dvs_obj:
                            host_vmnic_facts['dvswitch'][dvs_obj.name] = []
                        for proxy_nic in proxy_config.spec.backing.pnicSpec:
                            proxy_switch_vmnics.append(proxy_nic.pnicDevice)
                            if dvs_obj:
                                host_vmnic_facts['dvswitch'][dvs_obj.name].append(proxy_nic.pnicDevice)

                used_vmics = proxy_switch_vmnics + vswitch_vmnics
                host_vmnic_facts['used'] = used_vmics
                host_vmnic_facts['available'] = [pnic.device for pnic in nw_config.pnic if pnic.device not in used_vmics]

            hosts_vmnic_facts[host.name] = host_vmnic_facts
        return hosts_vmnic_facts