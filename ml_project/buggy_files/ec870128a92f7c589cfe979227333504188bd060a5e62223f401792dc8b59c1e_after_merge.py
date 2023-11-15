    def finalize_config(self, dps):
        """Perform consistency checks after initial config parsing."""

        def resolve_port_no(port_name):
            """Resolve port by name or number."""
            if port_name in port_by_name:
                return port_by_name[port_name].number
            elif port_name in self.ports:
                return port_name
            return None

        def resolve_vlan(vlan_name):
            """Resolve VLAN by name or VID."""
            if vlan_name in vlan_by_name:
                return vlan_by_name[vlan_name]
            elif vlan_name in self.vlans:
                return self.vlans[vlan_name]
            return None

        def resolve_stack_dps():
            """Resolve DP references in stacking config."""
            port_stack_dp = {}
            for port in self.stack_ports:
                stack_dp = port.stack['dp']
                port_stack_dp[port] = dp_by_name[stack_dp]
            for port, dp in list(port_stack_dp.items()):
                port.stack['dp'] = dp
                stack_port_name = port.stack['port']
                port.stack['port'] = dp.ports[stack_port_name]

        def resolve_mirror_destinations():
            """Resolve mirror port references and destinations."""
            mirror_from_port = {}
            for port in list(self.ports.values()):
                if port.mirror is not None:
                    if port.mirror in port_by_name:
                        mirror_from_port[port] = port_by_name[port.mirror]
                    else:
                        mirror_from_port[self.ports[port.mirror]] = port
            for port, mirror_destination_port in list(mirror_from_port.items()):
                port.mirror = mirror_destination_port.number
                mirror_destination_port.mirror_destination = True

        def resolve_names_in_acls():
            """Resolve config references in ACLs."""
            for acl in list(self.acls.values()):
                for rule_conf in acl.rules:
                    for attrib, attrib_value in list(rule_conf.items()):
                        if attrib == 'actions':
                            if 'meter' in attrib_value:
                                meter_name = attrib_value['meter']
                                assert meter_name in self.meters
                            if 'mirror' in attrib_value:
                                port_name = attrib_value['mirror']
                                port_no = resolve_port_no(port_name)
                                # in V2 config, we might have an ACL that does
                                # not apply to a DP.
                                if port_no is not None:
                                    attrib_value['mirror'] = port_no
                                    port = self.ports[port_no]
                                    port.mirror_destination = True
                            if 'output' in attrib_value:
                                output_values = attrib_value['output']
                                if 'port' in output_values:
                                    port_name = output_values['port']
                                    port_no = resolve_port_no(port_name)
                                    if port_no is not None:
                                        output_values['port'] = port_no
                                if 'failover' in output_values:
                                    failover = output_values['failover']
                                    resolved_ports = []
                                    for port_name in failover['ports']:
                                        port_no = resolve_port_no(port_name)
                                        if port_no is not None:
                                            resolved_ports.append(port_no)
                                    failover['ports'] = resolved_ports

        def resolve_acls():
            """Resolve ACL references in config."""

            def build_acl(acl, vid=None):
                """Check that ACL can be built from config."""
                if acl.rules:
                    assert valve_acl.build_acl_ofmsgs(
                        [acl], self.wildcard_table,
                        valve_of.goto_table(self.wildcard_table),
                        2**16, self.meters, acl.exact_match,
                        vlan_vid=vid)

            for vlan in list(self.vlans.values()):
                if vlan.acl_in:
                    if vlan.acl_in in self.acls:
                        vlan.acl_in = self.acls[vlan.acl_in]
                        build_acl(vlan.acl_in, vid=1)
                    else:
                        assert False, 'Unconfigured vlan for %s' % self.name
            for port in list(self.ports.values()):
                if port.acl_in:
                    if port.acl_in in self.acls:
                        port.acl_in = self.acls[port.acl_in]
                        build_acl(port.acl_in)
                    else:
                        assert False, 'Unconfigured acl for %s' % self.name

        def resolve_vlan_names_in_routers():
            """Resolve VLAN references in routers."""
            dp_routers = {}
            for router_name, router in list(self.routers.items()):
                vlans = []
                for vlan_name in router.vlans:
                    vlan = resolve_vlan(vlan_name)
                    if vlan is not None:
                        vlans.append(vlan)
                if len(vlans) > 1:
                    dp_router = copy.copy(router)
                    dp_router.vlans = vlans
                    dp_routers[router_name] = dp_router
            self.routers = dp_routers

        assert self.ports, 'no interfaces defined for %s' % self.name
        assert self.vlans, 'no VLANs referenced by interfaces in %s' % self.name

        port_by_name = {}
        for port in list(self.ports.values()):
            port_by_name[port.name] = port
        dp_by_name = {}
        for dp in dps:
            dp_by_name[dp.name] = dp
        vlan_by_name = {}
        for vlan in list(self.vlans.values()):
            vlan_by_name[vlan.name] = vlan

        resolve_stack_dps()
        resolve_mirror_destinations()
        resolve_vlan_names_in_routers()
        resolve_names_in_acls()
        resolve_acls()

        for port in list(self.ports.values()):
            port.finalize()
        for vlan in list(self.vlans.values()):
            vlan.finalize()
        for acl in list(self.acls.values()):
            acl.finalize()
        for router in list(self.routers.values()):
            router.finalize()
        self.finalize()