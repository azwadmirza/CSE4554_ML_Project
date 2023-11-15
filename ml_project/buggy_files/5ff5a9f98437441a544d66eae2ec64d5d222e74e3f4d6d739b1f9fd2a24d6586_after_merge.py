    def _parse_instance(self, raw_instance):
        instance_dict = {}
        instance_dict['id'] = get_non_provider_id(raw_instance['name'])
        instance_dict['project_id'] = self.project_id
        instance_dict['name'] = raw_instance['name']
        instance_dict['description'] = self._get_description(raw_instance)
        instance_dict['creation_timestamp'] = raw_instance['creationTimestamp']
        instance_dict['zone'] = raw_instance['zone'].split('/')[-1]
        instance_dict['tags'] = raw_instance['tags']
        instance_dict['status'] = raw_instance['status']
        instance_dict['zone_url_'] = raw_instance['zone']
        instance_dict['network_interfaces'] = raw_instance['networkInterfaces']
        instance_dict['service_accounts'] = raw_instance.get('serviceAccounts', [])
        instance_dict['deletion_protection_enabled'] = raw_instance['deletionProtection']
        instance_dict['block_project_ssh_keys_enabled'] = self._is_block_project_ssh_keys_enabled(raw_instance)
        instance_dict['oslogin_enabled'] = self._is_oslogin_enabled(raw_instance)
        instance_dict['ip_forwarding_enabled'] = raw_instance['canIpForward']
        instance_dict['serial_port_enabled'] = self._is_serial_port_enabled(raw_instance)
        instance_dict['has_full_access_cloud_apis'] = self._has_full_access_to_all_cloud_apis(raw_instance)
        instance_dict['disks'] = InstanceDisks(self.facade, raw_instance)
        return instance_dict['id'], instance_dict