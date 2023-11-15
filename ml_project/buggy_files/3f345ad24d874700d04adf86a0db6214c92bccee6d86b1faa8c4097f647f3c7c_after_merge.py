    def get_lldp_neighbors_detail(self, interface=''):
        """Detailed view of the LLDP neighbors."""
        lldp_neighbors = {}

        lldp_table = junos_views.junos_lldp_neighbors_detail_table(self.device)
        try:
            lldp_table.get()
        except RpcError as rpcerr:
            # this assumes the library runs in an environment
            # able to handle logs
            # otherwise, the user just won't see this happening
            log.error('Unable to retrieve the LLDP neighbors information:')
            log.error(rpcerr.message)
            return {}
        interfaces = lldp_table.get().keys()

        # get lldp neighbor by interface rpc for EX Series, QFX Series, J Series
        # and SRX Series is get-lldp-interface-neighbors-information,
        # and rpc for M, MX, and T Series is get-lldp-interface-neighbors
        # ref1: https://apps.juniper.net/xmlapi/operTags.jsp  (Junos 13.1 and later)
        # ref2: https://www.juniper.net/documentation/en_US/junos12.3/information-products/topic-collections/junos-xml-ref-oper/index.html  (Junos 12.3) # noqa
        # Exceptions:
        # EX9208    personality = SWITCH    RPC: <get-lldp-interface-neighbors><interface-device>
        lldp_table.GET_RPC = 'get-lldp-interface-neighbors'
        if self.device.facts.get('personality') not in ('MX', 'M', 'PTX', 'T')\
           and self.device.facts.get('model') not in ('EX9208', 'QFX10008'):
            # Still need to confirm for QFX10002 and other EX series
            lldp_table.GET_RPC = 'get-lldp-interface-neighbors-information'

        for interface in interfaces:
            if 'EX9208' in self.device.facts.get('model'):
                lldp_table.get(interface_device=interface)
            elif self.device.facts.get('personality') not in ('MX', 'M', 'PTX', 'T'):
                lldp_table.get(interface_name=interface)
            else:
                lldp_table.get(interface_device=interface)
            for item in lldp_table:
                if interface not in lldp_neighbors.keys():
                    lldp_neighbors[interface] = []
                lldp_neighbors[interface].append({
                    'parent_interface': item.parent_interface,
                    'remote_port': item.remote_port,
                    'remote_chassis_id': napalm.base.helpers.convert(
                        napalm.base.helpers.mac, item.remote_chassis_id, item.remote_chassis_id),
                    'remote_port_description': napalm.base.helpers.convert(
                        py23_compat.text_type, item.remote_port_description),
                    'remote_system_name': item.remote_system_name,
                    'remote_system_description': item.remote_system_description,
                    'remote_system_capab': item.remote_system_capab,
                    'remote_system_enable_capab': item.remote_system_enable_capab
                })

        return lldp_neighbors