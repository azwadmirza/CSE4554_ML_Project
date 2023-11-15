    def compare_subnets(self):
        """
        Compare user subnets with current ELB subnets

        :return: bool True if they match otherwise False
        """

        subnet_mapping_id_list = []
        subnet_mappings = []

        # Check if we're dealing with subnets or subnet_mappings
        if self.subnets is not None:
            # Convert subnets to subnet_mappings format for comparison
            for subnet in self.subnets:
                subnet_mappings.append({'SubnetId': subnet})

        if self.subnet_mappings is not None:
            # Use this directly since we're comparing as a mapping
            subnet_mappings = self.subnet_mappings

        # Build a subnet_mapping style struture of what's currently
        # on the load balancer
        for subnet in self.elb['AvailabilityZones']:
            this_mapping = {'SubnetId': subnet['SubnetId']}
            for address in subnet.get('LoadBalancerAddresses', []):
                if 'AllocationId' in address:
                    this_mapping['AllocationId'] = address['AllocationId']
                    break

            subnet_mapping_id_list.append(this_mapping)

        return set(frozenset(mapping.items()) for mapping in subnet_mapping_id_list) == set(frozenset(mapping.items()) for mapping in subnet_mappings)