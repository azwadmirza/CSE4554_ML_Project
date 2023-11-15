    def get_data(self):
        d = {
            'id': self.name,
            'create_time': self.instance['InstanceCreateTime'],
            'engine': self.instance['Engine'],
            'engine_version': self.instance['EngineVersion'],
            'license_model': self.instance['LicenseModel'],
            'character_set_name': self.instance['CharacterSetName'],
            'allocated_storage': self.instance['AllocatedStorage'],
            'publicly_accessible': self.instance['PubliclyAccessible'],
            'latest_restorable_time': self.instance['LatestRestorableTime'],
            'status': self.status,
            'availability_zone': self.instance['AvailabilityZone'],
            'secondary_availability_zone': self.instance['SecondaryAvailabilityZone'],
            'backup_retention': self.instance['BackupRetentionPeriod'],
            'backup_window': self.instance['PreferredBackupWindow'],
            'maintenance_window': self.instance['PreferredMaintenanceWindow'],
            'auto_minor_version_upgrade': self.instance['AutoMinorVersionUpgrade'],
            'read_replica_source_dbinstance_identifier': self.instance['ReadReplicaSourceDBInstanceIdentifier'],
            'multi_zone': self.instance['MultiAZ'],
            'instance_type': self.instance['DBInstanceClass'],
            'username': self.instance['MasterUsername'],
            'db_name': self.instance['DBName'],
            'iops': self.instance['Iops'],
            'replication_source': self.instance['ReadReplicaSourceDBInstanceIdentifier']
        }
        if self.instance['DBParameterGroups'] is not None:
            parameter_groups = []
            for x in self.instance['DBParameterGroups']:
                parameter_groups.append({'parameter_group_name': x['DBParameterGroupName'], 'parameter_apply_status': x['ParameterApplyStatus']})
            d['parameter_groups'] = parameter_groups
        if self.instance['OptionGroupMemberships'] is not None:
            option_groups = []
            for x in self.instance['OptionGroupMemberships']:
                option_groups.append({'status': x['Status'], 'option_group_name': x['OptionGroupName']})
            d['option_groups'] = option_groups
        if self.instance['PendingModifiedValues'] is not None:
            pdv = self.instance['PendingModifiedValues']
            d['pending_modified_values'] = {
                'multi_az': pdv['MultiAZ'],
                'master_user_password': pdv['MasterUserPassword'],
                'port': pdv['Port'],
                'iops': pdv['Iops'],
                'allocated_storage': pdv['AllocatedStorage'],
                'engine_version': pdv['EngineVersion'],
                'backup_retention_period': pdv['BackupRetentionPeriod'],
                'db_instance_class': pdv['DBInstanceClass'],
                'db_instance_identifier': pdv['DBInstanceIdentifier']
            }
        if self.instance["DBSubnetGroup"] is not None:
            dsg = self.instance["DBSubnetGroup"]
            db_subnet_groups = {}
            db_subnet_groups['vpc_id'] = dsg['VpcId']
            db_subnet_groups['name'] = dsg['DBSubnetGroupName']
            db_subnet_groups['status'] = dsg['SubnetGroupStatus'].lower()
            db_subnet_groups['description'] = dsg['DBSubnetGroupDescription']
            db_subnet_groups['subnets'] = []
            for x in dsg["Subnets"]:
                db_subnet_groups['subnets'].append({
                    'status': x['SubnetStatus'].lower(),
                    'identifier': x['SubnetIdentifier'],
                    'availability_zone': {
                        'name': x['SubnetAvailabilityZone']['Name'],
                        'provisioned_iops_capable': x['SubnetAvailabilityZone']['ProvisionedIopsCapable']
                    }
                })
            d['db_subnet_groups'] = db_subnet_groups
        if self.instance["VpcSecurityGroups"] is not None:
            d['vpc_security_groups'] = ','.join(x['VpcSecurityGroupId'] for x in self.instance['VpcSecurityGroups'])
        if "Endpoint" in self.instance and self.instance["Endpoint"] is not None:
            d['endpoint'] = self.instance["Endpoint"].get('Address', None)
            d['port'] = self.instance["Endpoint"].get('Port', None)
        else:
            d['endpoint'] = None
            d['port'] = None
        if self.instance["DBName"]:
            d['DBName'] = self.instance['DBName']
        return d