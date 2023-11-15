    def query_service_type_for_vmks(self, host_system, service_type):
        """
        Function to return list of VMKernels
        Args:
            host_system: Host system managed object
            service_type: Name of service type

        Returns: List of VMKernel which belongs to that service type

        """
        vmks_list = []
        query = None
        try:
            query = host_system.configManager.virtualNicManager.QueryNetConfig(service_type)
        except vim.fault.HostConfigFault as config_fault:
            self.module.fail_json(msg="Failed to get all VMKs for service type %s due to"
                                      " host config fault : %s" % (service_type, to_native(config_fault.msg)))
        except vmodl.fault.InvalidArgument as invalid_argument:
            self.module.fail_json(msg="Failed to get all VMKs for service type %s due to"
                                      " invalid arguments : %s" % (service_type, to_native(invalid_argument.msg)))
        except Exception as e:
            self.module.fail_json(msg="Failed to get all VMKs for service type %s due to"
                                      "%s" % (service_type, to_native(e)))

        if not query.selectedVnic:
            return vmks_list
        selected_vnics = [vnic for vnic in query.selectedVnic]
        vnics_with_service_type = [vnic.device for vnic in query.candidateVnic if vnic.key in selected_vnics]
        return vnics_with_service_type