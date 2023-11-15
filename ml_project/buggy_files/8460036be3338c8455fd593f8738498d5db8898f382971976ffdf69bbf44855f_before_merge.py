    def parse_instance(self, global_params, region, reservation):
        """
        Parse a single EC2 instance

        :param global_params:           Parameters shared for all regions
        :param region:                  Name of the AWS region
        :param instance:                Cluster
        """
        for i in reservation['Instances']:
            instance = {}
            vpc_id = i['VpcId'] if 'VpcId' in i and i['VpcId'] else ec2_classic
            manage_dictionary(self.vpcs, vpc_id, VPCConfig(self.vpc_resource_types))
            instance['reservation_id'] = reservation['ReservationId']
            instance['id'] = i['InstanceId']
            get_name(i, instance, 'InstanceId')
            get_keys(i, instance, ['KeyName', 'LaunchTime', 'InstanceType', 'State', 'IamInstanceProfile', 'SubnetId'])
            # Network interfaces & security groups
            manage_dictionary(instance, 'network_interfaces', {})
            for eni in i['NetworkInterfaces']:
                nic = {}
                get_keys(eni, nic, ['Association', 'Groups', 'PrivateIpAddresses', 'SubnetId', 'Ipv6Addresses'])
                instance['network_interfaces'][eni['NetworkInterfaceId']] = nic
            self.vpcs[vpc_id].instances[i['InstanceId']] = instance